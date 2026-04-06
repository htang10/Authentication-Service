from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidCredentials(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid email or password."
    default_code = "INVALID_CREDENTIALS"


class EmailNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Email not exist."
    default_code = "EMAIL_NOT_EXIST"


class EmailNotVerified(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email not verified."
    default_code = "EMAIL_NOT_VERIFIED"


class EmailAlreadyVerified(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email already verified."
    default_code = "EMAIL_ALREADY_VERIFIED"


class EmailVerificationError(Exception):
    pass

