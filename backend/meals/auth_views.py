from __future__ import annotations

from dataclasses import asdict

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_services import (
    AuthResult,
    AuthService,
    EmailAlreadyExists,
    InvalidCredentials,
    InvalidResetToken,
)


def _set_auth_cookies(response: Response, refresh: RefreshToken) -> None:
    access_token: str = str(refresh.access_token)
    refresh_token: str = str(refresh)

    max_age_access: int = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
    max_age_refresh: int = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())

    cookie_kwargs: dict = {
        "httponly": True,
        "secure": settings.JWT_AUTH_COOKIE_SECURE,
        "samesite": settings.JWT_AUTH_COOKIE_SAMESITE,
        "path": "/",
    }
    response.set_cookie(settings.JWT_AUTH_COOKIE, access_token, max_age=max_age_access, **cookie_kwargs)
    response.set_cookie(settings.JWT_AUTH_REFRESH_COOKIE, refresh_token, max_age=max_age_refresh, **cookie_kwargs)


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path="/")
    response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE, path="/")


auth_service = AuthService()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email: str = request.data.get("email", "").strip().lower()
        password: str = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result: AuthResult = auth_service.login(email, password)
        except InvalidCredentials:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({"user": asdict(result.user)}, status=status.HTTP_200_OK)
        _set_auth_cookies(response, result.refresh)
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        _clear_auth_cookies(response)
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email: str = request.data.get("email", "").strip().lower()
        password: str = request.data.get("password", "")
        first_name: str = request.data.get("first_name", "").strip()
        last_name: str = request.data.get("last_name", "").strip()

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result: AuthResult = auth_service.register(email, password, first_name, last_name)
        except EmailAlreadyExists:
            return Response(
                {"error": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response({"user": asdict(result.user)}, status=status.HTTP_201_CREATED)
        _set_auth_cookies(response, result.refresh)
        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user_data = auth_service.get_profile(request.user.id)
        return Response(asdict(user_data))


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        refresh_token: str | None = request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)
        if not refresh_token:
            return Response(
                {"error": "No refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            response = Response({"detail": "Token refreshed."}, status=status.HTTP_200_OK)
            _set_auth_cookies(response, refresh)
            return response
        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email: str = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        auth_service.request_password_reset(email)

        return Response(
            {"detail": "If that email is registered, you'll receive a reset link shortly."}
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        uid: str = request.data.get("uid", "")
        token: str = request.data.get("token", "")
        new_password: str = request.data.get("password", "")

        if not uid or not token or not new_password:
            return Response(
                {"error": "uid, token, and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            auth_service.reset_password(uid, token, new_password)
        except InvalidResetToken:
            return Response(
                {"error": "This reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Password updated successfully."})
