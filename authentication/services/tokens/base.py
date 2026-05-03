from hashlib import sha512


def hash_secret(value: str) -> str:
    """Hashes a value using SHA-512 and returns the hex digest."""
    return sha512(value.encode("utf-8")).hexdigest()
