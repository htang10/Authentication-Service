from celery import shared_task

from authentication.models import User
from authentication.services.mailing import (
    send_email_change_link,
    send_email_verification_link,
    send_otp_email,
    send_password_reset_link,
)


@shared_task
def send_email_verification_link_task(email: str) -> None:
    user = User.objects.get(email=email)
    send_email_verification_link(user)


@shared_task
def send_password_reset_link_task(email: str) -> None:
    user = User.objects.get(email=email)
    send_password_reset_link(user)


@shared_task
def send_email_change_link_task(email: str) -> None:
    user = User.objects.get(email=email)
    send_email_change_link(user)


@shared_task
def send_otp_email_task(email: str) -> None:
    send_otp_email(email)
