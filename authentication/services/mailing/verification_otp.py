import logging
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException

from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string

from authentication.exceptions import MailingServiceFailure
from authentication.services.mailing.base import dispatch_mail
from authentication.services.tokens import generate_code, save_code
from authentication.utils import format_expiry, generate_plain_text_from_html

logger = logging.getLogger(__name__)


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


def generate_otp(email, expiry: int | float) -> None:
    try:
        # The newest code is used for validation
        code, hashed_code = generate_code()
        save_code(
            hashed_code, email, expiry
        )  # Automatically invalidate previous unused codes
        send_code(email, code, expiry)
    except (TemplateDoesNotExist, TemplateSyntaxError) as template_error:
        # Your template is missing or broken
        logger.error(f"Template error: {template_error}")
        raise MailingServiceFailure
    except SMTPAuthenticationError as auth_error:
        # Email credentials are wrong
        logger.error(f"Authentication error: {auth_error}")
        raise MailingServiceFailure
    except SMTPConnectError as connect_error:
        # Can't reach the mail server
        logger.error(f"Connection error: {connect_error}")
        raise MailingServiceFailure
    except SMTPException as unexpected_smtp_error:
        # Catch-all for any other SMTP failure
        logger.error(f"Unexpected error: {unexpected_smtp_error}")
        raise MailingServiceFailure
    except DatabaseError as db_error:
        # Token failed to save
        logger.exception(f"Database error: {db_error}")  # Trace failed queries
        raise MailingServiceFailure


def send_otp_email(email: str) -> None:
    generate_otp(email, expiry=1 / 6)  # 10 minutes
