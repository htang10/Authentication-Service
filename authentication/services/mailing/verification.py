import logging
import secrets
from datetime import timedelta
from hashlib import sha512
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.exceptions import EmailVerificationError
from authentication.models import Token, User

logger = logging.getLogger(__name__)

# Map purpose to template + subject + url path
TOKEN_EMAIL_CONFIG = {
    Token.Purpose.VERIFICATION: {
        "subject": "Please Activate Your Account",
        "txt_template": "emails/verification_email.txt",
        "html_template": "emails/verification_email.html",
        "url_path": "/auth/verify/",
    },
    Token.Purpose.PASSWORD_RESET: {
        "subject": "Reset Your Password",
        "txt_template": "",
        "html_template": "",
        "url_path": "/auth/reset-password/",
    },
    Token.Purpose.EMAIL_CHANGE: {
        "subject": "Confirmation link to change your email",
        "html_template": "",
        "url_path": "",
    },
}


def generate_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
    return token, hashed_token


def save_token(
    hashed_token: str, user: User, purpose: Token.Purpose, expiry: int | float
) -> Token:
    hours = int(expiry)
    minutes = (expiry - hours) * 60
    expires_at = timezone.now() + timedelta(hours=hours, minutes=minutes)

    return Token.objects.create(
        user=user, token=hashed_token, purpose=purpose, expires_at=expires_at
    )


def send_email(email: str, token: str, purpose: Token.Purpose):
    config = TOKEN_EMAIL_CONFIG[purpose]

    url = f"{settings.FRONTEND_URL}{config['url_path']}?token={token}&purpose={purpose}"

    text_content = render_to_string(config["txt_template"], {"url": url})
    html_content = render_to_string(config["html_template"], {"url": url})

    msg = EmailMultiAlternatives(
        subject=config["subject"],
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        body=text_content,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def generate_email(user: User, purpose: Token.Purpose, expiry: int | float = 24):
    # A user may request multiple verification emails
    # Invalidate all previous unused tokens
    Token.objects.filter(user=user, purpose=purpose, used_at__isnull=True).update(
        expires_at=timezone.now()
    )

    try:
        # The newest token is used for validation
        token, hashed_token = generate_token()
        save_token(hashed_token, user, purpose, expiry)
        send_email(user.email, token, purpose)
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


def send_verification_link(user: User):
    generate_email(user, Token.Purpose.VERIFICATION)


def send_password_reset_link(user: User):
    generate_email(user, Token.Purpose.PASSWORD_RESET, expiry=1 / 6)


def send_email_change_link(user: User):
    generate_email(user, Token.Purpose.EMAIL_CHANGE)


def verify_token(token: str, purpose: Token.Purpose):
    if not token:
        raise ValidationError({"error": "Token is required."})
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
    token_obj = (
        Token.objects.select_related("user")
        .filter(
            token=hashed_token,
            purpose=purpose,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        .first()
    )

    if not token_obj:
        raise ValidationError({"error": "Invalid or expired token."})

    token_obj.used_at = timezone.now()
    token_obj.save()

    token_obj.user.email_verified_at = timezone.now()
    token_obj.user.save()
