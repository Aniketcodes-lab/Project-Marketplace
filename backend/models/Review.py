from django.db import models
from models.Project import Project
from models.User import AdminLogin, User, UserManager



class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=5)  # 1–5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'buyer')

    def __str__(self):
        return f"{self.project.title} - {self.rating}⭐"
    
    @classmethod
    def create_review(cls, project, buyer, rating, comment=None):
        review, created = cls.objects.get_or_create(project=project, buyer=buyer)
        review.rating = rating
        review.comment = comment
        review.save()
        return review
    
    @classmethod
    def get_average_rating(cls, project):
        reviews = cls.objects.filter(project=project)
        if not reviews.exists():
            return 0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / reviews.count()
    
    @classmethod
    def get_reviews(cls, project):
        return cls.objects.filter(project=project)
    
    @classmethod
    def get_review(cls, project, buyer):
        return cls.objects.filter(project=project, buyer=buyer).first()
    
    @classmethod
    def delete_review(cls, project, buyer):
        return cls.objects.filter(project=project, buyer=buyer).delete()
    
    @classmethod
    def update_review(cls, project, buyer, rating=None, comment=None):
        review = cls.objects.filter(project=project, buyer=buyer).first()
        if not review:
            return None
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        review.save()
        return review
    
    @classmethod
    def has_reviewed(cls, project, buyer):
        return cls.objects.filter(project=project, buyer=buyer).exists()
    
    @classmethod
    def get_reviews_by_buyer(cls, buyer):
        return cls.objects.filter(buyer=buyer)
    
    @classmethod
    def get_reviews_by_rating(cls, project, rating):
        return cls.objects.filter(project=project, rating=rating)
    
    @classmethod
    def get_recent_reviews(cls, project, limit=5):
        return cls.objects.filter(project=project).order_by('-created_at')[:limit]
    
    