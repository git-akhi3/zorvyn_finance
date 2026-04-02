from rest_framework.response import Response


class APIResponse:

    @staticmethod
    def success(message, data=None, status_code=200):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data
            },
            status=status_code
        )

    @staticmethod
    def error(message, error_code=None, status_code=400, data=None):
        return Response(
            {
                "status": "error",
                "message": message,
                "error_code": error_code,
                "data": data
            },
            status=status_code
        )
