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
    
    def update_status(self, new_status):
        if new_status in dict(CustomRequestStatus):
            self.status = new_status
            self.save()
    
    @classmethod
    def create_request(cls, buyer, title, description, budget):
        request = cls.objects.create(
            buyer=buyer,
            title=title,
            description=description,
            budget=budget
        )
        request.mark_as_open()
        request.save()
        return request
    
    @classmethod
    def get_requests_by_buyer(cls, buyer):
        return cls.objects.filter(buyer=buyer).order_by('-created_at')
    
    @classmethod
    def get_requests_by_status(cls, status):
        return cls.objects.filter(status=status).order_by('-created_at')
    
    @classmethod
    def get_all_requests(cls):
        return cls.objects.all().order_by('-created_at')
    
    def mark_as_completed(self):
        self.status = "completed"
        self.save()

    def mark_as_cancelled(self):
        self.status = "cancelled"
        self.save()
    
    def mark_as_in_progress(self):
        self.status = "in_progress"
        self.save()
    
    def mark_as_closed(self):
        self.status = "closed"
        self.save()

    def mark_as_open(self):
        self.status = "open"
        self.save()

    def reopen_request(self):
        self.status = "open"
        self.save()

    def close_request(self):
        self.status = "closed"
        self.save()

    def cancel_request(self):
        self.status = "cancelled"
        self.save()
