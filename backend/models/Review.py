from django.db import models
from models.Project import Project
from models.User import AdminLogin, User, UserManager



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

