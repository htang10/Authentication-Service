from authentication.models import Token
from authentication.services.tokens.ott import hash_token, mark_used_token


def reset_password(token_str: str, new_password: str) -> None:
    hashed_token = hash_token(token_str)
    token = Token.objects.get(token=hashed_token)
    user = token.user

    user.set_password(new_password)
    user.save()

    mark_used_token(token)
