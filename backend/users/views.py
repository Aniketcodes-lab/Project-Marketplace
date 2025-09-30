from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from models.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializer import *
import re
import logging
from rest_framework.permissions import AllowAny

logger = logging.getLogger("django")

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh.access_token.set_exp(None)

    return {
        "access": str(refresh.access_token),
    }

def get_host(request):
    host = request.META.get("HTTP_HOST")
    return f"http://{host}"


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request, format= None):
        email = request.data.get("email")
        
        # Check if email is already in use
        if email and User.objects.filter(email=email).exists():
            logger.warning(f"Email address in use: {email}")
            return Response(
                {
                    "msg": "This email address is already in use"},
                    status=status.HTTP_409_CONFLICT,
            )
            
        #Validation the registration data
        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            
            logger.info(f"New user registered: {user.email} with ID: {user.id}")
            return Response({
                "token" : token.get("access"),
                "user":serializer.data,
                "msg": "registration Successfully"
            },
            status = status.HTTP_201_CREATED
            )
            
        logger.error(f"Registration failed with errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, format=None):
        request_data = request.data.copy()
        email_or_phone = request_data.get("emailOrPhone")
        logger.info(f"Received login attempt from: {email_or_phone}")

        if re.match(r"^\d{10,15}$", email_or_phone):  # Phone number check
            request_data["phone_number"] = self.format_phone_number(email_or_phone)
            logger.debug(f"Formatted phone number: {request_data['phone_number']}")
        elif re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_or_phone):  # Email check
            request_data["email"] = email_or_phone
            logger.debug(f"Received email: {request_data['email']}")
        else:
            logger.warning(f"Invalid email or phone number format: {email_or_phone}")
            return Response({"errors": {"non_field_errors": ["Invalid email or phone number format"]}},
                            status=status.HTTP_400_BAD_REQUEST)

        # Custom serializer and validation
        serializer = UserLoginSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            phone_number = serializer.validated_data.get("phone_number")
            logger.info(f"Validated login credentials for email: {email or 'N/A'}")

            try:
                user = (
                    User.objects.get(email=email) if email else User.objects.get(phone_number=phone_number)
                )
                if check_password(password, user.password):
                    logger.info(f"Login successful for user ID: {user.id}")
                    token = self.get_tokens_for_user(user)
                    # Commenting out the email verification part
                    """
                    email_verification = EmailVerification.objects.filter(
                        user=user, verification_type="email_change"
                    )
                    if email_verification.exists():
                        if email_verification[0].is_expired():
                            email_verification.delete()
                            serialized_data["email_changed"] = False
                            logger.info(f"Email verification expired, email_changed set to False for user ID: {user.id}")
                        else:
                            serialized_data["email_changed"] = True
                            logger.info(f"Email verification pending for user ID: {user.id}")
                    else:
                        serialized_data["email_changed"] = False
                        logger.info(f"No email verification found for user ID: {user.id}")
                    """
                    # End of EmailVerification block

                    serialized_data = UserRegistrationSerializer(user).data
                    serialized_data["default_password"] = user.default_password
                    logger.info(f"Returning token and user data for user ID: {user.id}")
                    return Response({
                        "token": token["access"],
                        "msg": "Login successful",
                        "user": serialized_data
                    }, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"Incorrect password attempt for user: {email_or_phone}")
                    return Response({"errors": {"non_field_errors": ["Incorrect credentials"]}},
                                    status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                logger.error(f"User not found with provided email or phone number")
                return Response({"errors": {"non_field_errors": ["User not found"]}}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def format_phone_number(self, cleaned):
        match = re.match(r"^(\d{0,3})(\d{0,3})(\d{0,4})$", cleaned)
        if match:
            area_code = match.group(1)
            central_office_code = match.group(2)
            line_number = match.group(3)
            if not central_office_code:
                return area_code
            else:
                return f"{area_code}-{central_office_code}" + (
                    f"-{line_number}" if line_number else ""
                )
        return cleaned