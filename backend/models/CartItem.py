from django.db import models
from models.Project import Project
from models.User import AdminLogin, User, UserManager

class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", limit_choices_to={'role': 'buyer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'project')

    def __str__(self):
        return f"{self.buyer.email} -> {self.project.title}"
     
