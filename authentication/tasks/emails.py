from celery import shared_task

from authentication.models import User
from authentication.services.mailing.verification import (
    send_email_change_link,
    send_email_verification_link,
    send_password_reset_link,
)


@shared_task
def send_email_verification_link_task(user_id: int) -> None:
    user = User.objects.get(id=user_id)
    send_email_verification_link(user)


@shared_task
def send_password_reset_link_task(user_id: int) -> None:
    user = User.objects.get(id=user_id)
    send_password_reset_link(user)


@shared_task
def send_email_change_link_task(user_id: int) -> None:
    user = User.objects.get(id=user_id)
    send_email_change_link(user)
