from hashlib import sha512


def hash_secret(value: str) -> str:
    return sha512(value.encode("utf-8")).hexdigest()
