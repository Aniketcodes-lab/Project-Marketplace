from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

difficulty_choices = [
    ("beginner", "Beginner"), 
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]

ProjectApprovalRequestStatus = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected")
]

CustomRequestStatus = [
    ("open", "Open"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]

def getTime():
    return datetime.now().strftime("%I:%M %p")


class AdminLogin(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None, role="buyer"):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_contributor = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class Technology(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class ApplicationCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Project(models.Model):
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", limit_choices_to={'role': 'contributor'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.ManyToManyField(Technology)
    category = models.ManyToManyField(ApplicationCategory)
    difficulty = models.CharField(max_length=50, choices=difficulty_choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    readme_file = models.FileField(upload_to='project/readme/', blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)
    github_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProjectApprovalRequest(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="approval_request")
    status = models.CharField(max_length=20, choices=ProjectApprovalRequestStatus, default="pending")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    admin_comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.project.title} - {self.status}"


class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'project')

    def __str__(self):
        return f"{self.buyer.email} -> {self.project.title}"
     

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.project.title}"


class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'buyer'})
    rating = models.IntegerField(default=5)  # 1–5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'buyer')

    def __str__(self):
        return f"{self.project.title} - {self.rating}⭐"


class ProjectInquiry(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquiries", null=True, blank=True)
    technology = models.ManyToManyField(Technology, related_name="inquiries", blank=True)
    application_category = models.ManyToManyField(ApplicationCategory, related_name="inquiries", blank=True)
    message = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry by {self.name}"


class CustomRequest(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests", limit_choices_to={'role': 'buyer'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CustomRequestStatus, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request: {self.title} ({self.status})"


class Bid(models.Model):
    request = models.ForeignKey(CustomRequest, on_delete=models.CASCADE, related_name="bids")
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'contributor'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'contributor')

    def __str__(self):
        return f"Bid {self.amount} by {self.contributor.email}"


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
    def create_token(cls, user, data=None):
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


