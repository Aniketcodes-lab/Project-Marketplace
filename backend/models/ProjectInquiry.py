from django.db import models
from models.Technology import Technology
from models.ApplicationCategory import ApplicationCategory
from models.User import AdminLogin, User, UserManager


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
    
    @classmethod
    def create_inquiry(cls, name, email, message, user=None, technology_list=None, application_category_list=None, budget=None):
        inquiry = cls.objects.create(
            name=name,
            email=email,
            message=message,
            user=user,
            budget=budget
        )
        if technology_list:
            inquiry.technology.set(technology_list)
        if application_category_list:
            inquiry.application_category.set(application_category_list)
        inquiry.save()
        return inquiry

