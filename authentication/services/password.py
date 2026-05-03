from authentication.models import Token
from authentication.services.tokens import hash_secret, mark_token_used


def reset_password(token_str: str, new_password: str) -> None:
    hashed_token = hash_secret(token_str)
    token = Token.objects.get(token=hashed_token)
    user = token.user

    user.set_password(new_password)
    user.save()

    mark_token_used(token)
