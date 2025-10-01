from django.db import models
from models.Project import Project

ProjectApprovalRequestStatus = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected")
]

class ProjectApprovalRequest(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="approval_request")
    status = models.CharField(max_length=20, choices=ProjectApprovalRequestStatus, default="pending")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    admin_comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.project.title} - {self.status}"
    
    def approve(self, admin_comment=None):
        self.status = "approved"
        self.reviewed_at = models.DateTimeField(auto_now=True)
        self.admin_comment = admin_comment
        self.save()

    def reject(self, admin_comment=None):
        self.status = "rejected"
        self.reviewed_at = models.DateTimeField(auto_now=True)
        self.admin_comment = admin_comment
        self.save()

    @classmethod
    def create_request(cls, project):
        request, created = cls.objects.get_or_create(project=project)
        if not created:
            request.status = "pending"
            request.reviewed_at = None
            request.admin_comment = None
            request.save()
        return request

