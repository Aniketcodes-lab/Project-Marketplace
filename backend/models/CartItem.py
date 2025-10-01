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
    
    @classmethod
    def add_to_cart(cls, buyer, project):
        cart_item, created = cls.objects.get_or_create(buyer=buyer, project=project)
        return cart_item
        
    @classmethod
    def remove_from_cart(cls, buyer, project):
        return cls.objects.filter(buyer=buyer, project=project).delete()
    
    @classmethod
    def get_cart_items(cls, buyer):
        return cls.objects.filter(buyer=buyer).select_related('project').order_by('-added_at')
    
    @classmethod
    def clear_cart(cls, buyer):
        return cls.objects.filter(buyer=buyer).delete()
    
    
     
