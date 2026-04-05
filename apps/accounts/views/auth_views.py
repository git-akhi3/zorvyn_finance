import logging

from drf_spectacular.utils import extend_schema
from rest_framework import serializers

from apps.core.utils.swagger_helpers import auth_schema, create_response_serializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.accounts.constants import AuthErrorCodes, AuthMessages, CommonMessages
from apps.accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from apps.accounts.services import AuthService
from apps.accounts.throttling import LoginThrottle, RegisterThrottle
from apps.core.utils.api_response import APIResponse
from apps.core.utils.exceptions import (
    InternalServerErrorException,
    NotAuthenticatedException,
    UnauthorizedAccessException,
)


logger = logging.getLogger(__name__)


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthPayloadSerializer(serializers.Serializer):
    user = UserSerializer()
    tokens = TokenPairSerializer()


RegisterResponseSerializer = create_response_serializer(AuthPayloadSerializer, name_prefix='Register')
LoginResponseSerializer = create_response_serializer(AuthPayloadSerializer, name_prefix='Login')


@auth_schema
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    @extend_schema(request=RegisterSerializer, responses={201: RegisterResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning("Register validation failed", extra={"errors": serializer.errors})
            return APIResponse.error(
                message=CommonMessages.VALIDATION_ERROR,
                data=serializer.errors,
                status_code=400,
            )

        try:
            result = AuthService.register(serializer.validated_data)
        except InternalServerErrorException as exc:
            logger.exception("Register failed due to internal service error")
            return APIResponse.error(
                message=str(exc),
                status_code=500,
            )

        return APIResponse.success(
            message=AuthMessages.REGISTER_SUCCESS,
            data={"user": UserSerializer(result["user"]).data, "tokens": result["tokens"]},
            status_code=201,
        )


@auth_schema
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning("Login validation failed", extra={"errors": serializer.errors})
            return APIResponse.error(
                message=CommonMessages.VALIDATION_ERROR,
                data=serializer.errors,
                status_code=400,
            )

        try:
            result = AuthService.login(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except NotAuthenticatedException:
            logger.warning("Login failed: invalid credentials")
            return APIResponse.error(
                message=AuthMessages.INVALID_CREDENTIALS,
                error_code=AuthErrorCodes.INVALID_CREDENTIALS,
                status_code=401,
            )
        except UnauthorizedAccessException:
            logger.warning("Login blocked: inactive account")
            return APIResponse.error(
                message=AuthMessages.ACCOUNT_INACTIVE,
                error_code=AuthErrorCodes.ACCOUNT_INACTIVE,
                status_code=403,
            )

        return APIResponse.success(
            message=AuthMessages.LOGIN_SUCCESS,
            data={"user": UserSerializer(result["user"]).data, "tokens": result["tokens"]},
        )
