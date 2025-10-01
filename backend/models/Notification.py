from django.db import models
from models.User import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    data = models.JSONField(default=dict)
    # data = {
    #     "type": "order" / "review" / "message" / etc
    #     "message": "Your order has been shipped.",
    #     "related_id": 123,  # e.g., order ID, project ID, etc.
    #     "related_title": "Order #123",
    #     "related_url": "/orders/123",
    # }
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {'Read' if self.is_read else 'Unread'}"
    
    @classmethod
    def create_notification(cls, user, data={}):
        notification = cls.objects.create(user=user, data=data)
        return notification
    



