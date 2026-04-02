

from rest_framework.views import exception_handler

from apps.core.constants import GenericErrorCodes, GenericMessages
from apps.core.response import APIResponse


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        handlers = {
            400: (GenericMessages.VALIDATION_ERROR, GenericErrorCodes.VALIDATION_ERROR),
            401: (GenericMessages.UNAUTHORIZED, GenericErrorCodes.UNAUTHORIZED),
            403: (GenericMessages.PERMISSION_DENIED, GenericErrorCodes.PERMISSION_DENIED),
            404: (GenericMessages.NOT_FOUND, GenericErrorCodes.NOT_FOUND),
        }
        message, error_code = handlers.get(
            response.status_code,
            (GenericMessages.SERVER_ERROR, GenericErrorCodes.SERVER_ERROR)
        )
        return APIResponse.error(
            message=message,
            error_code=error_code,
            data=response.data if response.status_code == 400 else None,
            status_code=response.status_code
        )

    return response
