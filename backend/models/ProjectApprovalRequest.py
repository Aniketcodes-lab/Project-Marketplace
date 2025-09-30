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

