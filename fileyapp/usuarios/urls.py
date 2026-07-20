from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, OTPRequestView, RegisterView

app_name = 'usuarios'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
