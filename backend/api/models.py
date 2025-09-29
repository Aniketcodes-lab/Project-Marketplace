from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime

def getTime():
    return datetime.now().strftime("%I:%M %p")

# ----------------------------
# Custom User Manager
# ----------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    # def create_superuser(self, email, first_name, last_name, phone_number, password=None, **extra_fields):
    #     """
    #     Create and return a superuser with the given email, username, and password.
    #     """
    #     # Ensure that is_staff and is_superuser are True for superuser
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     # Pass all necessary fields, including first_name, last_name, and phone_number
    #     return self.create_user(email, first_name, last_name, phone_number, password, **extra_fields)



# ----------------------------
# Custom User Model
# ----------------------------
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('contributor', 'Contributor'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30 ,null=True, blank= True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank= True)
    bio = models.TextField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="buyer")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # for Django admin

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} ({self.role})"
    
# ----------------------------
# Project Model
# ----------------------------
class Project(models.Model):
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50, choices=[
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='project/')
    demo_url = models.URLField(blank=True, null= True)
    token_to_access = models.TextField(blank= True, null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default = False)
    rejected_reason = models.TextField(blank=True, null=True)  # last rejection reason
    
    def __str__(self):
        return self.title
    
# ----------------------------
# Admin Approval/Rejection Log
# ----------------------------
class ProjectApprovalLog(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="approaval_log")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'admin'})    
    status = models.CharField(max_length=20, choices=[
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ])
    comment = models.TextField(blank= True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.Project.title} - {self.status}"

# ----------------------------
# Cart
# ----------------------------
class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart",
                              limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'project')

    def __str__(self):
        return f"{self.buyer.email} -> {self.project.title}"
    
    
# ----------------------------
# Orders / Purchases
# ----------------------------
class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders",
                              limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.project.title}"


# ----------------------------
# Contributor Earnings
# ----------------------------
class Earning(models.Model):
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="earnings",
                                    limit_choices_to={'role': 'contributor'})
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Earning {self.amount} for {self.contributor.email}"


# ----------------------------
# Reviews & Ratings
# ----------------------------
class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE,
                              limit_choices_to={'role': 'buyer'})
    rating = models.IntegerField(default=5)  # 1–5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'buyer')

    def __str__(self):
        return f"{self.project.title} - {self.rating}⭐"


# ----------------------------
# Custom Project Requests
# ----------------------------
class CustomRequest(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests",
                              limit_choices_to={'role': 'buyer'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ], default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request: {self.title} ({self.status})"


class Bid(models.Model):
    request = models.ForeignKey(CustomRequest, on_delete=models.CASCADE, related_name="bids")
    contributor = models.ForeignKey(User, on_delete=models.CASCADE,
                                    limit_choices_to={'role': 'contributor'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'contributor')

    def __str__(self):
        return f"Bid {self.amount} by {self.contributor.email}"