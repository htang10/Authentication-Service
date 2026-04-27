from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidCredentials(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid credentials."
    default_code = "INVALID_CREDENTIALS"


class EmailNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Email not exist."
    default_code = "EMAIL_NOT_EXIST"


class EmailAlreadyExists(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email already exists."
    default_code = "EMAIL_ALREADY_EXISTS"


class EmailNotVerified(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email not verified."
    default_code = "EMAIL_NOT_VERIFIED"


class EmailAlreadyVerified(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email already verified."
    default_code = "EMAIL_ALREADY_VERIFIED"


class EmailVerificationError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Failed to send email."
    default_code = "EMAIL_VERIFICATION_ERROR"
