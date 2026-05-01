import html2text


def normalize_email(email: str) -> str:
    """Converts all letters in email address to lowercase."""
    return email.strip().lower()


def get_client_ip(request) -> str:
    """Retrieves the client IP address of the current request.

    Prefers X-Forwarded-For header for proxy compatibility.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def convert_expiry(expiry: int | float) -> tuple[int, int]:
    """Converts a fractional hour value to a (hours, minutes) tuple."""
    hours = int(expiry)
    minutes = int((expiry - hours) * 60)

    return hours, minutes


def format_expiry(expiry: int | float) -> str:
    """Formats a fractional hour value as a human-readable string.

    Expiry is expected to be either whole hours (e.g. 1, 2) or a sub-hour fraction (e.g. 0.5),
    not a mix of both (e.g. 1.5 is not a valid input).

    Examples:
        format_expiry(1) -> "1 hour"
        format_expiry(2) -> "2 hours"
        format_expiry(0.5) -> "30 minutes"
    """
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
