from django.db import models
from datetime import datetime
from models.Technology import Technology
from models.ApplicationCategory import ApplicationCategory
from models.User import AdminLogin, User, UserManager


difficulty_choices = [
    ("beginner", "Beginner"), 
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]


def getTime():
    return datetime.now().strftime("%I:%M %p")


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

