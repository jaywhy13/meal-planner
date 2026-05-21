from django.urls import path

from .auth_views import (
    ForgotPasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    ResetPasswordView,
    TokenRefreshView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
    path("register", RegisterView.as_view(), name="auth-register"),
    path("profile", ProfileView.as_view(), name="auth-profile"),
    path("token/refresh", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("forgot-password", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("reset-password", ResetPasswordView.as_view(), name="auth-reset-password"),
]
