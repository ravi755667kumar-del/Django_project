from django.core.mail import send_mail
from django.conf import settings


def send_reset_email(email, reset_link):

    subject = "Brew Haven Password Reset"

    message = f"""
Hello,

You requested to reset your Brew Haven password.

Click the link below:

{reset_link}

If you didn't request this, please ignore this email.

Thank you,
Brew Haven Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )