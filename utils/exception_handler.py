from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Normalizes all DRF exception responses to {"error": <message>} format."""
    response = exception_handler(exc, context)

    if response is None:
        return None

    data = response.data

    if "detail" in data:
        response.data = {"error": data["detail"]}
    elif "non_field_errors" in data:
        response.data = {"error": data["non_field_errors"][0]}
    elif isinstance(data, list):
        response.data = {"error": data[0]}
    else:
        response.data = {"error": {field: errors[0] for field, errors in data.items()}}

    return response
