from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime

def getTime():
    return datetime.now().strftime("%I:%M %p")

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
    
