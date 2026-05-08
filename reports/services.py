import csv
from io import BytesIO, StringIO

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from accounts.models import User
from attendance.models import Attendance
from leaves.models import LeaveRequest
from tasks.models import Task


def date_range_from_request(request):
    today = timezone.localdate()
    start = request.GET.get("start") or today.replace(day=1).isoformat()
    end = request.GET.get("end") or today.isoformat()
    return start, end


def attendance_queryset(request):
    start, end = date_range_from_request(request)
    qs = Attendance.objects.select_related("user", "office").filter(date__range=[start, end])
    user_id = request.GET.get("user")
    if user_id and request.user.is_admin_role:
        qs = qs.filter(user_id=user_id)
    if not request.user.is_admin_role:
        qs = qs.filter(user=request.user)
    return qs


def attendance_rows(qs):
    for record in qs:
        yield [
            record.date,
            record.user.employee_id,
            record.user.full_name,
            record.status,
            record.punch_in_at,
            record.punch_out_at,
            record.working_hours,
            record.punch_in_distance_m,
            record.punch_out_distance_m,
        ]


def export_attendance_csv(request):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Employee ID", "Name", "Status", "Punch In", "Punch Out", "Working Hours", "In Distance(m)", "Out Distance(m)"])
    writer.writerows(attendance_rows(attendance_queryset(request)))
    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="attendance-report.csv"'
    return response


def export_attendance_xlsx(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    sheet.append(["Date", "Employee ID", "Name", "Status", "Punch In", "Punch Out", "Working Hours", "In Distance(m)", "Out Distance(m)"])
    for row in attendance_rows(attendance_queryset(request)):
        sheet.append(row)
    stream = BytesIO()
    workbook.save(stream)
    response = HttpResponse(stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="attendance-report.xlsx"'
    return response


def export_attendance_pdf(request):
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=A4)
    width, height = A4
    y = height - 48
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(48, y, "OfficeFlow Attendance Report")
    y -= 28
    pdf.setFont("Helvetica", 9)
    for row in attendance_rows(attendance_queryset(request)[:45]):
        text = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[6]}h"
        pdf.drawString(48, y, text[:110])
        y -= 16
        if y < 48:
            pdf.showPage()
            y = height - 48
            pdf.setFont("Helvetica", 9)
    pdf.save()
    response = HttpResponse(stream.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="attendance-report.pdf"'
    return response


def productivity_snapshot(user=None):
    today = timezone.localdate()
    start = today.replace(day=1)
    users = User.objects.filter(status=User.EmploymentStatus.ACTIVE, role=User.Role.STAFF)
    if user:
        users = users.filter(pk=user.pk)
    results = []
    for staff in users:
        attendance_count = Attendance.objects.filter(user=staff, date__range=[start, today], status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE, Attendance.Status.HALF_DAY]).count()
        working_hours = sum(record.working_hours for record in Attendance.objects.filter(user=staff, date__range=[start, today]))
        tasks = Task.objects.filter(assigned_to=staff, created_at__date__range=[start, today])
        completed = tasks.filter(status=Task.Status.COMPLETED).count()
        task_rate = round((completed / tasks.count()) * 100, 2) if tasks.exists() else 0
        leave_days = sum(leave.days for leave in LeaveRequest.objects.filter(user=staff, start_date__range=[start, today], status=LeaveRequest.Status.APPROVED))
        attendance_percentage = round((attendance_count / max(today.day, 1)) * 100, 2)
        score = round((attendance_percentage * 0.45) + (task_rate * 0.45) + (min(working_hours / 160 * 100, 100) * 0.10), 2)
        results.append(
            {
                "user": staff,
                "attendance_percentage": attendance_percentage,
                "working_hours": round(working_hours, 2),
                "task_completion_rate": task_rate,
                "leave_days": leave_days,
                "productivity_score": score,
                "insight": smart_productivity_summary(attendance_percentage, task_rate, score),
            }
        )
    return results


def smart_productivity_summary(attendance_percentage, task_rate, score):
    if score >= 85:
        return "Strong overall performance with reliable attendance and task delivery."
    if attendance_percentage < 70:
        return "Attendance consistency is the biggest opportunity this month."
    if task_rate < 60:
        return "Task completion pace needs attention; review workload and blockers."
    return "Performance is stable with room to improve consistency."
