from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User
from authentication.utils import get_client_ip


def get_user_by_refresh_token(token):
    """Retrieves a user by refresh token"""
    user_id = RefreshToken(token)["user_id"]
    user = User.objects.get(pk=user_id)
    return user


def update_user_login_metadata(user, request):
    """
    Updates the user login metadata including timestamp, ip address, user agent and medium.
    """
    now = timezone.now()
    user.last_login_time = now
    user.last_active = now
    user.last_login_ip = get_client_ip(request)
    user.last_login_uagent = request.META.get("HTTP_USER_AGENT", "")
    user.last_login_medium = "email"
    user.save(update_fields=[
        "last_login_time", "last_active", "last_login_ip",
        "last_login_uagent", "last_login_medium"
    ])
    return user


def update_user_logout_metadata(user, request):
    """
    Updates the user logout metadata including timestamp and ip address
    """
    user.last_logout_time = timezone.now()
    user.last_logout_ip = get_client_ip(request)
    user.save(update_fields=["last_logout_time", "last_logout_ip"])
    return user
