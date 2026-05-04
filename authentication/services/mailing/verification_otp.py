from django.template.loader import render_to_string

from authentication.services.mailing.base import dispatch_mail, handle_mailing_errors
from authentication.services.tokens import generate_code, save_code
from authentication.utils import format_expiry, generate_plain_text_from_html

TEMPLATE_NAME = "emails/code.html"


def mail_otp_code(email: str, code: str, expiry: int | float) -> None:
    """Sends a one-time verification code to the given email."""
    expiry_display = format_expiry(expiry)
    subject = "Confirmation code to log in your account"
    html_content = render_to_string(
        TEMPLATE_NAME,
        {
            "code": code,
            "expiry": expiry_display,
        },
    )
    text_content = generate_plain_text_from_html(html_content)

    dispatch_mail(
        recipients=[email],
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


def generate_otp_email(email: str, expiry: int | float) -> None:
    """Generates and sends an OTP to the given email address.

    All previous unused codes for the user are invalidated before the new one is created.
    """
    with handle_mailing_errors():
        code, hashed_code = generate_code()
        save_code(hashed_code, email, expiry)
        mail_otp_code(email, code, expiry)


def send_login_otp(email: str) -> None:
    generate_otp_email(email, expiry=1 / 6)  # 10 minutes
