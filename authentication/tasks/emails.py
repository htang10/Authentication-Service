from celery import shared_task

from authentication.services.mailing import (
    send_email_change_link,
    send_email_verification_link,
    send_login_otp,
    send_password_reset_link,
)


@shared_task
def send_email_verification_link_task(email: str) -> None:
    send_email_verification_link(email)


@shared_task
def send_password_reset_link_task(email: str) -> None:
    send_password_reset_link(email)


@shared_task
def send_email_change_link_task(email: str) -> None:
    send_email_change_link(email)


@shared_task
def send_otp_email_task(email: str) -> None:
    send_login_otp(email)
