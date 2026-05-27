from django.urls import path

from .auth_views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    TokenRefreshView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
    path("register", RegisterView.as_view(), name="auth-register"),
    path("profile", ProfileView.as_view(), name="auth-profile"),
    path("token/refresh", TokenRefreshView.as_view(), name="auth-token-refresh"),
]
