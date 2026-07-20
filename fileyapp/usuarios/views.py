import logging

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notificaciones.services.email import EmailDeliveryError, send_otp_email

from .models import OTPCode
from .serializers import (
    LogoutSerializer,
    OTPLoginSerializer,
    OTPRequestSerializer,
    RegisterSerializer,
    tokens_for,
)

logger = logging.getLogger(__name__)

# Generic response for OTP requests so we never reveal whether an email exists.
_GENERIC_OTP_RESPONSE = {
    'detail': 'Si el correo está registrado, se ha enviado un código de acceso.'
}


def _issue_and_send_otp(user):
    """Create an OTP for ``user`` and email it. Returns True on success."""
    otp, raw_code = OTPCode.objects.create_for_user(user)
    try:
        send_otp_email(user.email, raw_code)
    except EmailDeliveryError:
        logger.exception('Could not deliver OTP email to %s', user.email)
        return False
    return True


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-send an OTP so the user can log in immediately.
        _issue_and_send_otp(user)

        return Response(
            {
                'detail': 'Cuenta creada. Se ha enviado un código de acceso a tu correo.',
                'email': user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(username=email).first() or \
            User.objects.filter(email=email).first()
        if user is not None and user.is_active:
            _issue_and_send_otp(user)

        # Always the same response, regardless of whether the account exists.
        return Response(_GENERIC_OTP_RESPONSE, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(tokens_for(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_205_RESET_CONTENT)
