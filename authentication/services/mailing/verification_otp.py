from django.template.loader import render_to_string

from authentication.services.mailing.base import dispatch_mail, handle_mailing_errors
from authentication.services.tokens import generate_code, save_code
from authentication.utils import format_expiry, generate_plain_text_from_html


def send_code(email: str, code: str, expiry: int | float) -> None:
    expiry_display = format_expiry(expiry)
    subject = "Confirmation code to log in your account"
    html_content = render_to_string(
        "emails/verification_code.html",
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


def generate_otp(email: str, expiry: int | float) -> None:
    with handle_mailing_errors():
        # The newest code is used for validation
        code, hashed_code = generate_code()
        save_code(
            hashed_code, email, expiry
        )  # Automatically invalidate previous unused codes
        send_code(email, code, expiry)


def send_otp_email(email: str) -> None:
    generate_otp(email, expiry=1 / 6)  # 10 minutes
