def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_client_ip(request) -> str:
    """Retrieves the client ip address of the current request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
