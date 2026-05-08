from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.tokens import email_verification_token


def send_verification_email(request, user):
    if user.email_verified or not user.email:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    path = reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
    url = request.build_absolute_uri(path)
    send_mail(
        "Verify your OfficeFlow email",
        f"Welcome to OfficeFlow. Verify your email here: {url}",
        None,
        [user.email],
        fail_silently=True,
    )
