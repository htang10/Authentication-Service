import logging
from contextlib import contextmanager
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError

from authentication.exceptions import MailingServiceFailure

logger = logging.getLogger(__name__)


def dispatch_mail(
    *, recipients: list[str], subject: str, html_content: str, text_content: str
) -> None:
    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        body=text_content,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@contextmanager
def handle_mailing_errors():
    """A context manager that catches template errors, SMTP errors and database error.

    Raises:
        MailingServiceFailure
    """
    try:
        yield
    except (TemplateDoesNotExist, TemplateSyntaxError) as e:
        logger.error(f"Template error: {e}")
        raise MailingServiceFailure
    except SMTPAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise MailingServiceFailure
    except SMTPConnectError as e:
        logger.error(f"Connection error: {e}")
        raise MailingServiceFailure
    except SMTPException as e:
        logger.error(f"Unexpected SMTP error: {e}")
        raise MailingServiceFailure
    except DatabaseError as e:
        logger.exception(f"Database error: {e}")
        raise MailingServiceFailure
