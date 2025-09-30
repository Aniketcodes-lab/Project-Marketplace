from django.db import models
from models.User import User


CustomRequestStatus = [
    ("open", "Open"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]



class CustomRequest(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests", limit_choices_to={'role': 'buyer'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CustomRequestStatus, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request: {self.title} ({self.status})"

