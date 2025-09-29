from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
#------------------------Common Views-------------------------------

# -------------------- new folder structure -----------------------------
    path('', include('api.views.auth.urls')),        # For authentication (login, register)
    path('', include('api.views.contributor.urls')),  # For contributor-related routes
]
