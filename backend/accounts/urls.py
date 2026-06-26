from django.urls import path
from .views import (
    SendPasswordResetEmailView,
    UserChangePasswordView,
    UserLoginView,
    UserLogoutView,
    UserPasswordResetView,
    UserProfileView,
    UserRegistrationView,
    VerifyEmailView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', UserChangePasswordView.as_view(), name='change-password'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]