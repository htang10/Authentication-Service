import logging
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException

from django.conf import settings
from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string

from authentication.exceptions import EmailVerificationError
from authentication.models import Token, User
from authentication.services.mailing.base import dispatch_mail
from authentication.services.tokens.verification import (
    generate_token,
    invalidate_past_tokens,
    save_token,
)

logger = logging.getLogger(__name__)

# Map purpose to template + subject + url path
VERIFICATION_EMAIL_CONFIG = {
    Token.Purpose.VERIFICATION: {
        "subject": "Please Activate Your Account",
        "html_template": "emails/verification_email.html",
        "txt_template": "emails/verification_email.txt",
        "url": "/auth/verify/",
    },
    Token.Purpose.PASSWORD_RESET: {
        "subject": "Reset Your Password",
        "html_template": "",
        "txt_template": "",
        "url": "/auth/reset-password/",
    },
    Token.Purpose.EMAIL_CHANGE: {
        "subject": "Confirmation link to change your email",
        "html_template": "",
        "url": "",
    },
}


def send_verification_email(email: str, token: str, purpose: Token.Purpose) -> None:
    config = VERIFICATION_EMAIL_CONFIG.get(purpose)

    verification_url = (
        f"{settings.FRONTEND_URL}{config["url"]}?token={token}&purpose={purpose}"
    )
    subject = config["subject"]
    html_content = render_to_string(
        config["html_template"], {"verification_url": verification_url}
    )
    text_content = render_to_string(
        config["txt_template"], {"verification_url": verification_url}
    )

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
        send_verification_email(user.email, token, purpose)
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
    generate_verification_email(user, Token.Purpose.VERIFICATION)


def send_password_reset_link(user: User) -> None:
    generate_verification_email(user, Token.Purpose.PASSWORD_RESET, expiry=1 / 6)


def send_email_change_link(user: User) -> None:
    generate_verification_email(user, Token.Purpose.EMAIL_CHANGE)
