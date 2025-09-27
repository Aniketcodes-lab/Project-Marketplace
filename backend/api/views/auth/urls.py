from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login-view'),
    path('register/', UserRegistrationView.as_view(), name='register-view'),
]