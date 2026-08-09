from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def send_reset_email(email, reset_link):
    """Send password reset email via Brevo SMTP."""

    subject = "Brew Haven — Password Reset Request"

    # Plain text version (fallback)
    text_body = f"""Hello,

You requested to reset your Brew Haven password.

Click the link below to reset it:
{reset_link}

This link will expire shortly. If you didn't request this, please ignore this email.

Thank you,
Brew Haven Team
"""

    # HTML version (looks great in inbox)
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 30px;
                border: 1px solid #e0e0e0; border-radius: 10px; background: #fafafa;">
        <h2 style="color: #5c3317; text-align: center;">☕ Brew Haven</h2>
        <hr style="border: none; border-top: 1px solid #ddd;" />
        <p style="font-size: 16px; color: #333;">Hello,</p>
        <p style="font-size: 15px; color: #555;">
            You requested to reset your <strong>Brew Haven</strong> password.
            Click the button below to set a new password:
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}"
               style="background-color: #5c3317; color: #fff; padding: 12px 30px;
                      text-decoration: none; border-radius: 6px; font-size: 15px;">
                Reset My Password
            </a>
        </div>
        <p style="font-size: 13px; color: #999; text-align: center;">
            If you didn't request this, please ignore this email. This link will expire shortly.
        </p>
        <hr style="border: none; border-top: 1px solid #ddd;" />
        <p style="font-size: 12px; color: #bbb; text-align: center;">
            &copy; Brew Haven Team
        </p>
    </div>
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        print(f"\n[!] BREVO RESET EMAIL ERROR: {e}\n")
        raise   # Re-raise so the background thread logs it properly


def send_otp_email(name, email, otp):
    """Send OTP verification email via Brevo SMTP."""

    subject = "Your Brew Haven Verification Code"

    text_body = f"""Hi {name},

Your Brew Haven OTP is: {otp}

It is valid for 1 minute. Do not share it with anyone.

— Brew Haven Team
"""

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 30px;
                border: 1px solid #e0e0e0; border-radius: 10px; background: #fafafa;">
        <h2 style="color: #5c3317; text-align: center;">☕ Brew Haven</h2>
        <hr style="border: none; border-top: 1px solid #ddd;" />
        <p style="font-size: 16px; color: #333;">Hi <strong>{name}</strong>,</p>
        <p style="font-size: 15px; color: #555;">
            Your verification code for <strong>Brew Haven</strong> is:
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 40px; font-weight: bold; color: #5c3317;
                         letter-spacing: 10px; background: #fff3e0; padding: 15px 30px;
                         border-radius: 8px; border: 2px dashed #5c3317;">
                {otp}
            </span>
        </div>
        <p style="font-size: 13px; color: #999; text-align: center;">
            ⏱️ This code is valid for <strong>1 minute</strong>. Do not share it with anyone.
        </p>
        <hr style="border: none; border-top: 1px solid #ddd;" />
        <p style="font-size: 12px; color: #bbb; text-align: center;">
            &copy; Brew Haven Team
        </p>
    </div>
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        print(f"\n[!] BREVO OTP EMAIL ERROR: {e}\n")
        raise