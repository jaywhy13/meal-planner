from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
        if not access_token:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return self.get_user(validated_token), validated_token
