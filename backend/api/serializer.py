from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=False, allow_blank=True)
    phone_number = serializers.CharField(
        max_length=15, required=False, allow_blank=True
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "phone_number"]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone_number", "profile_picture", "bio", "role", "password", "password_confirm"]
        extra_kwargs = {
            'bio': {'required': False},
            'profile_picture': {'required': False},
            'role': {'required': False, 'default': 'buyer'},  # Optional, defaults to 'buyer'
        }

    def validate(self, data):
        # Ensure that passwords match
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise ValidationError({"password_confirm": "Passwords do not match."})

        # Optionally, you can add password validation logic here
        # validate_password(password)  # If you want to validate password strength

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # Remove password_confirm from validated data

        # Create the user instance and hash the password using set_password()
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number'),
            profile_picture=validated_data.get('profile_picture'),
            bio=validated_data.get('bio'),
            role=validated_data.get('role', 'buyer'),
        )
        # Use set_password to hash the password
        user.set_password(validated_data['password'])
        user.save()

        return user
