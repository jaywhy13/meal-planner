from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


class EmailClient:
    def send_password_reset(
        self,
        recipient_email: str,
        recipient_name: str,
        reset_url: str,
    ) -> None:
        send_mail(
            subject="Reset your Meal Planner password",
            message=(
                f"Hi {recipient_name},\n\n"
                f"Click the link below to reset your password:\n\n{reset_url}\n\n"
                "This link expires in 24 hours. If you didn't request a reset, "
                "ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
        )
