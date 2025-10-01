from django.db import models
from models.CustomRequest import CustomRequest
from models.Notification import Notification
from models.Order import Order
from models.Project import Project
from models.ProjectApprovalRequest import ProjectApprovalRequest
from models.ProjectInquiry import ProjectInquiry
from models.Review import Review
from models.Token import Token
from models.CartItem import CartItem
from models.Technology import Technology
from models.ApplicationCategory import ApplicationCategory
from models.User import AdminLogin, User, UserManager



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
    
    @classmethod
    def place_bid(cls, request, contributor, amount, message=None):
        bid, created = cls.objects.get_or_create(
            request=request,
            contributor=contributor,
            defaults={'amount': amount, 'message': message}
        )
        if not created:
            bid.amount = amount
            bid.message = message
            bid.save()
        return bid
    
    @classmethod
    def get_bids_for_request(cls, request):
        return cls.objects.filter(request=request).order_by('-created_at')
    
    @classmethod
    def get_bids_by_contributor(cls, contributor):
        return cls.objects.filter(contributor=contributor).order_by('-created_at')
    
    def update_bid(self, amount=None, message=None):
        if amount is not None:
            self.amount = amount
        if message is not None:
            self.message = message
        self.save()
        return self


