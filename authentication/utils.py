import html2text


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_client_ip(request) -> str:
    """Retrieves the client ip address of the current request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def convert_expiry(expiry: int | float) -> tuple[int, int]:
    """Converts the expiry time to hours and minutes."""
    hours = int(expiry)
    minutes = int((expiry - hours) * 60)

    return hours, minutes


def format_expiry(expiry: int | float) -> str:
    hours, minutes = convert_expiry(expiry)

    if hours:
        if hours > 1:
            display = f"{hours} hours"
        else:
            display = f"{hours} hour"
    else:
        display = f"{minutes} minutes"

    return display


def generate_plain_text_from_html(html: str) -> str:
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    return converter.handle(html)
