from authentication.models import Token
from authentication.services.tokens import hash_secret, mark_used_token


def reset_password(token_str: str, new_password: str) -> None:
    hashed_token = hash_secret(token_str)
    token = Token.objects.get(token=hashed_token)
    user = token.user

    user.set_password(new_password)
    user.save()

    mark_used_token(token)
