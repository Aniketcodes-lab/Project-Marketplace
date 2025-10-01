from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from models.User import AdminLogin, User, UserManager



class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data = models.JSONField(default=dict)
    # data = {
    #     "type": "order" / "review" / "message" / etc
    # }
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"
    
    @staticmethod
    def _get_default_duration(duration):
        return duration or timedelta(hours=settings.TOKEN_VALIDATION_DURATION_IN_HOURS)

    def is_expired(self, duration=None):
        duration = self._get_default_duration(duration)
        return timezone.now() > self.created_at + duration

    def time_left(self, duration=None):
        duration = self._get_default_duration(duration)
        remaining = (self.created_at + duration) - timezone.now()
        return max(timedelta(0), remaining)

    def refresh(self):
        self.token = uuid.uuid4()
        self.created_at = timezone.now()
        self.save()
        return self, self.token

    def delete_token(self):
        self.delete()

    @classmethod
    def create_token(cls, user, data=dict()):
        token = cls.objects.create(user=user, data=data or {})
        return token, token.token

    @classmethod
    def validate_token(cls, token_str, duration=None):
        try:
            token = cls.objects.get(token=token_str)
            if token.is_expired(duration):
                token.delete()
                return None
            return token
        except cls.DoesNotExist:
            return None


