from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    @staticmethod
    def success(message, data=None, status_code=status.HTTP_200_OK):
        return Response({"message": message, "data": data, "status": True}, status=status_code)

    @staticmethod
    def error(message, error_code=None, data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {"message": message, "error_code": error_code, "data": data, "status": False},
            status=status_code,
        )


class ApiResponse(Response):

    def __init__(self, data=None, message="success",
                 status_code=status.HTTP_200_OK, success=True, **kwargs):
        standard_format = {
            "message": message,
            "data": data,
            "status": success,
        }
        super().__init__(standard_format, status=status_code, **kwargs)
