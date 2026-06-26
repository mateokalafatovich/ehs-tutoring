from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import *
from .emails import Util
from django.contrib.auth import authenticate
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

   
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password']
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'), 
            email=email, 
            password=password
        )
        
        if not user:
            raise serializers.ValidationError({"status": "error", "message": "Email or password doesn't match. Please try again."})
    
        if not user.is_verified:
            raise serializers.ValidationError({"status": "error", "message": "Email is not verified. Please check your email for the OTP."})
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'role'
        ]
     
class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'new_password2']
        
    def validate(self, attrs):
        user = self.context.get('user')
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')

        if not check_password(old_password, user.password):
            raise serializers.ValidationError({"old_password": "Old password is not correct."})

        if new_password == old_password:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})
        
        if new_password != new_password2:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})

        return attrs
    
    def save(self, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return user
    
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email does not exist."})
        else:
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # Here you would typically send the email with the reset link containing uidb64 and token
            link = f"http://localhost:8000/api/accounts/reset-password/{uidb64}/{token}/"
            body = f"Hi {user.username},\nUse the link below to reset your password:\n{link}"
            Util.send_email({
                'email_subject': 'Reset your password',
                'email_body': body,
                'to_email': user.email,
            })
            return attrs

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uidb64 = self.context.get('uidb64')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError({"password": "Passwords do not match."})

            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({"token": "The reset link is invalid or has expired."})

            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            raise serializers.ValidationError({"token": "The reset link is invalid or has expired."})
        except TokenError as e:
            raise serializers.ValidationError({"token": "The reset link is invalid or has expired."})
        
class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Invalid or expired token."})