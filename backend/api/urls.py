from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
#------------------------Common Views-------------------------------

# -------------------- new folder structure -----------------------------
path('', include('api.views.auth.urls')),   # For register, login, authentication
path('', include('api.views.contributer.urls'))  
]