from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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
