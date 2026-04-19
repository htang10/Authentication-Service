import logging
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException

from django.conf import settings
from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string

from authentication.exceptions import EmailVerificationError
from authentication.models import Token, User
from authentication.services.mailing.base import dispatch_mail
from authentication.services.tokens.ott import (
    generate_token,
    invalidate_past_tokens,
    save_token,
)
from authentication.utils import format_expiry, generate_plain_text_from_html

logger = logging.getLogger(__name__)

# Map purpose to template + subject + url path
VERIFICATION_EMAIL_CONFIG = {
    Token.Purpose.SIGN_UP: {"subject": "Please Activate Your Account"},
    Token.Purpose.PASSWORD_RESET: {"subject": "Reset Your Password"},
    Token.Purpose.EMAIL_CHANGE: {"subject": "Confirmation link to change your email"},
}


def send_verification_email(
    email: str, token: str, purpose: Token.Purpose, expiry: int | float
) -> None:
    config = VERIFICATION_EMAIL_CONFIG.get(purpose)

    # Extract variables for template
    username = User.objects.get(email=email).display_name
    url = f"{settings.FRONTEND_URL}/auth/verify?token={token}&purpose={purpose}"
    expiry_display = format_expiry(expiry)

    # Configure email subject and body
    subject = config["subject"]
    html_content = render_to_string(
        "emails/verification.html",
        {
            "username": username,
            "purpose": purpose.value.replace("_", " "),
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


def generate_verification_email(
    user: User, purpose: Token.Purpose, expiry: int | float = 24
) -> None:
    # A user may request multiple verification emails
    # Invalidate all previous unused tokens
    invalidate_past_tokens(user, purpose)

    try:
        # The newest token is used for validation
        token, hashed_token = generate_token()
        save_token(hashed_token, user, purpose, expiry)
        send_verification_email(user.email, token, purpose, expiry)
    except (TemplateDoesNotExist, TemplateSyntaxError) as template_error:
        # Your template is missing or broken
        logger.error(f"Template error: {template_error}")
        raise EmailVerificationError
    except SMTPAuthenticationError as auth_error:
        # Email credentials are wrong
        logger.error(f"Authentication error: {auth_error}")
        raise EmailVerificationError
    except SMTPConnectError as connect_error:
        # Can't reach the mail server
        logger.error(f"Connection error: {connect_error}")
        raise EmailVerificationError
    except SMTPException as unexpected_smtp_error:
        # Catch-all for any other SMTP failure
        logger.error(f"Unexpected error: {unexpected_smtp_error}")
        raise EmailVerificationError
    except DatabaseError as db_error:
        # Token failed to save
        logger.exception(f"Database error: {db_error}")  # Trace failed queries
        raise EmailVerificationError


def send_email_verification_link(user: User) -> None:
    generate_verification_email(user, Token.Purpose.SIGN_UP)


def send_password_reset_link(user: User) -> None:
    generate_verification_email(user, Token.Purpose.PASSWORD_RESET, expiry=1)


def send_email_change_link(user: User) -> None:
    generate_verification_email(user, Token.Purpose.EMAIL_CHANGE)
