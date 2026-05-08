import base64
import binascii
import uuid
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from accounts.models import User
from attendance.models import Attendance, AttendanceAttempt, OfficeLocation
from core.utils import get_client_ip, haversine_distance_meters


class AttendanceValidationError(ValueError):
    pass


def active_office():
    office = OfficeLocation.objects.filter(is_active=True).order_by("created_at").first()
    if not office:
        raise AttendanceValidationError("No active office location is configured.")
    return office


def validate_office_location(latitude, longitude, accuracy_m=None):
    office = active_office()
    if latitude is None or longitude is None:
        raise AttendanceValidationError("Location permission is required.")
    if accuracy_m is not None and float(accuracy_m) > 120:
        raise AttendanceValidationError("GPS accuracy is too low. Move near a window and try again.")
    distance = haversine_distance_meters(latitude, longitude, office.latitude, office.longitude)
    if distance > office.radius_meters:
        raise AttendanceValidationError(f"You are {int(distance)}m away from {office.name}. Attendance is allowed within {office.radius_meters}m.")
    return office, distance


def decode_selfie(data_url):
    if not data_url:
        return None
    try:
        header, encoded = data_url.split(",", 1)
        extension = "jpg"
        if "png" in header:
            extension = "png"
        return ContentFile(base64.b64decode(encoded), name=f"selfie-{uuid.uuid4().hex}.{extension}")
    except (ValueError, TypeError, binascii.Error):
        raise AttendanceValidationError("Selfie image could not be processed.")


def attendance_status_for_now(office, timestamp):
    office_start = datetime.combine(timestamp.date(), office.start_time, tzinfo=timestamp.tzinfo)
    late_after = office_start + timedelta(minutes=office.late_grace_minutes)
    return Attendance.Status.LATE if timestamp > late_after else Attendance.Status.PRESENT


def log_attempt(user, action, request, allowed=False, reason="", office=None, latitude=None, longitude=None, accuracy_m=None, distance_m=None):
    return AttendanceAttempt.objects.create(
        user=user,
        office=office,
        action=action,
        allowed=allowed,
        reason=reason[:255],
        latitude=latitude,
        longitude=longitude,
        accuracy_m=accuracy_m,
        distance_m=distance_m,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )


def broadcast_attendance_event(event_type, attendance):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        "attendance",
        {
            "type": "attendance.event",
            "event": event_type,
            "user": attendance.user.full_name,
            "date": str(attendance.date),
            "status": attendance.status,
            "working_hours": attendance.working_hours,
        },
    )


@transaction.atomic
def punch_in(user, request, latitude, longitude, accuracy_m=None, selfie_data=None, notes=""):
    office = None
    distance = None
    try:
        office, distance = validate_office_location(latitude, longitude, accuracy_m)
        today = timezone.localdate()
        if Attendance.objects.filter(user=user, date=today, punch_in_at__isnull=False).exists():
            raise AttendanceValidationError("You have already punched in today.")
        now = timezone.now()
        attendance = Attendance.objects.create(
            user=user,
            office=office,
            date=today,
            punch_in_at=now,
            punch_in_latitude=latitude,
            punch_in_longitude=longitude,
            punch_in_distance_m=distance,
            gps_accuracy_m=accuracy_m,
            punch_in_ip=get_client_ip(request),
            punch_in_device=request.META.get("HTTP_USER_AGENT", ""),
            selfie=decode_selfie(selfie_data),
            status=attendance_status_for_now(office, now),
            notes=notes,
        )
        log_attempt(user, "in", request, True, "Allowed", office, latitude, longitude, accuracy_m, distance)
        broadcast_attendance_event("punch_in", attendance)
        return attendance
    except AttendanceValidationError as exc:
        log_attempt(user, "in", request, False, str(exc), office, latitude, longitude, accuracy_m, distance)
        raise


@transaction.atomic
def punch_out(user, request, latitude, longitude, accuracy_m=None, notes=""):
    office = None
    distance = None
    try:
        office, distance = validate_office_location(latitude, longitude, accuracy_m)
        today = timezone.localdate()
        attendance = Attendance.objects.select_for_update().filter(user=user, date=today).first()
        if not attendance or not attendance.punch_in_at:
            raise AttendanceValidationError("Punch in first before punching out.")
        if attendance.punch_out_at:
            raise AttendanceValidationError("You have already punched out today.")
        attendance.punch_out_at = timezone.now()
        attendance.punch_out_latitude = latitude
        attendance.punch_out_longitude = longitude
        attendance.punch_out_distance_m = distance
        attendance.punch_out_ip = get_client_ip(request)
        attendance.punch_out_device = request.META.get("HTTP_USER_AGENT", "")
        if notes:
            attendance.notes = f"{attendance.notes}\n{notes}".strip()
        attendance.refresh_work_seconds()
        attendance.save()
        log_attempt(user, "out", request, True, "Allowed", office, latitude, longitude, accuracy_m, distance)
        broadcast_attendance_event("punch_out", attendance)
        return attendance
    except AttendanceValidationError as exc:
        log_attempt(user, "out", request, False, str(exc), office, latitude, longitude, accuracy_m, distance)
        raise


def attendance_dashboard_stats(user=None):
    today = timezone.localdate()
    users = User.objects.filter(status=User.EmploymentStatus.ACTIVE, role=User.Role.STAFF)
    records = Attendance.objects.filter(date=today).select_related("user")
    if user:
        users = users.filter(pk=user.pk)
        records = records.filter(user=user)
    present = records.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE, Attendance.Status.HALF_DAY]).count()
    late = records.filter(status=Attendance.Status.LATE).count()
    absent = max(users.count() - present, 0)
    month_records = Attendance.objects.filter(date__year=today.year, date__month=today.month)
    if user:
        month_records = month_records.filter(user=user)
    return {
        "present": present,
        "late": late,
        "absent": absent,
        "working_hours": round((month_records.aggregate(total=Sum("work_seconds"))["total"] or 0) / 3600, 2),
        "monthly_present": month_records.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE, Attendance.Status.HALF_DAY]).count(),
        "monthly_late": month_records.filter(status=Attendance.Status.LATE).count(),
        "status_breakdown": list(month_records.values("status").annotate(count=Count("id")).order_by("status")),
    }
