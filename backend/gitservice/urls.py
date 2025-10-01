from django.urls import path
from .views import *

urlpatterns = [
    path("copy-repo/", CopyGitHubRepoView.as_view(), name="copy-repo"),
]