from django.shortcuts import render

# Create your views here.
from django.db.migrations import serializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from .serializers import *
from .emails import send_otp_email
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Deactivate account until it is verified
            user.save(updated_fields=['is_active'])
            send_otp_email(user.email, user.otp)
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response({"status": "success", "message": "User registered successfully. Please check your email for the OTP."}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp:
                    user.is_active = True
                    user.otp = None  # Clear the OTP after successful verification
                    user.save()
                    return Response({"status": "success", "message": "Email verified successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "error", "message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"status": "error", "message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = authenticate(
                request=self.request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                if not user.is_active:
                    return Response({"status": "error", "message": "Account is inactive. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)
                
                token = get_token_for_user(user)
                return Response({"status": "success", "message": "Login successful.", "token": token}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in after password change
            return Response({"status": "success", "message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Password reset failed. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
    
class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SendPasswordResetEmailSerializer
    
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"status": "success", "message": "Password reset email has been sent successfully. Please check your email inbox. or some check spam"}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, uid, token, *args, **kwargs):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uidb64': uid, 'token': token})
        if serializer.is_valid():
            return Response({"status": "success", "message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogoutView(APIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": "success", "message": "Logout successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)