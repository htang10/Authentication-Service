from django.conf import settings
from django.template.loader import render_to_string

from authentication.models import Token
from authentication.services.mailing.base import dispatch_mail, handle_mailing_errors
from authentication.services.tokens import (
    generate_token,
    invalidate_past_tokens,
    save_token,
)
from authentication.services.user import get_user_by_email
from authentication.utils import format_expiry, generate_plain_text_from_html

# Map purpose to template + subject + url path
CONFIG = {
    Token.Purpose.SIGN_UP: {
        "subject": "Please Activate Your Account",
        "content": "Verify email address",
    },
    Token.Purpose.PASSWORD_RESET: {
        "subject": "Reset Your Password",
        "content": "Set new password",
    },
    Token.Purpose.EMAIL_CHANGE: {
        "subject": "Confirmation link to change your email",
        "content": "Update email address",
    },
}


def send_link(
    email: str, token: str, purpose: Token.Purpose, expiry: int | float
) -> None:
    config = CONFIG[purpose]

    # Extract variables for template
    url = f"{settings.FRONTEND_URL}/auth/verify?token={token}&purpose={purpose}"
    expiry_display = format_expiry(expiry)

    # Configure email subject and body
    subject = config["subject"]
    html_content = render_to_string(
        "emails/verification_link.html",
        {
            "content": config["content"],
            "url": url,
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


def generate_link(email: str, purpose: Token.Purpose, expiry: int | float) -> None:
    user = get_user_by_email(email)
    # Invalidate all previous unused tokens
    invalidate_past_tokens(user, purpose)
    with handle_mailing_errors():
        # The newest token is used for validation
        token, hashed_token = generate_token()
        save_token(hashed_token, user, purpose, expiry)
        send_link(email, token, purpose, expiry)


def send_email_verification_link(email: str) -> None:
    generate_link(email, Token.Purpose.SIGN_UP, expiry=24)


def send_password_reset_link(email: str) -> None:
    generate_link(email, Token.Purpose.PASSWORD_RESET, expiry=1)


def send_email_change_link(email: str) -> None:
    generate_link(email, Token.Purpose.EMAIL_CHANGE, expiry=24)
