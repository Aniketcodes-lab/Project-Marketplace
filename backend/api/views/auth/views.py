from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password


class UserRegistrationView(APIView):
    pass

class LoginView(APIView):
    pass