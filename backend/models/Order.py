from django.db import models
from models.Project import Project
from models.User import AdminLogin, User, UserManager


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.project.title}"
    
    @classmethod
    def create_order(cls, buyer, project):
        order = cls.objects.create(buyer=buyer, project=project)
        return order
