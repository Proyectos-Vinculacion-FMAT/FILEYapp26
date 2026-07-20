from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPCode, Profile


def role_for(user):
    """The role claim the frontend uses to distinguish access."""
    return 'admin' if user.is_staff else 'user'


def tokens_for(user):
    """Build an access/refresh pair carrying the user's role claim."""
    refresh = RefreshToken.for_user(user)
    refresh['role'] = role_for(user)
    refresh['email'] = user.email
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'role': role_for(user),
    }


class RegisterSerializer(serializers.Serializer):
    """Self-registration for normal users (never admins)."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este correo.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_staff=False,
        )
        user.set_unusable_password()
        user.save()
        Profile.objects.create(user=user, phone=validated_data['phone'])
        return user


class OTPRequestSerializer(serializers.Serializer):
    """Request an OTP for an existing account (user or admin)."""

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class OTPLoginSerializer(serializers.Serializer):
    """Verify an OTP and return tokens."""

    email = serializers.EmailField()
    code = serializers.CharField(max_length=12)

    default_error_messages = {
        'invalid': 'Código o correo inválido, o el código ha expirado.',
    }

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        code = attrs['code'].strip()

        user = User.objects.filter(username=email).first() or \
            User.objects.filter(email=email).first()
        if user is None or not user.is_active:
            self.fail('invalid')

        otp = OTPCode.objects.filter(user=user, used=False).order_by('-created_at').first()
        if otp is None or not otp.verify(code):
            self.fail('invalid')

        otp.used = True
        otp.save(update_fields=['used'])

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Blacklist a refresh token."""

    refresh = serializers.CharField()

    default_error_messages = {
        'invalid': 'Token de actualización inválido o ya expirado.',
    }

    def validate(self, attrs):
        try:
            self.token = RefreshToken(attrs['refresh'])
        except Exception:
            self.fail('invalid')
        return attrs

    def save(self, **kwargs):
        try:
            self.token.blacklist()
        except Exception:
            self.fail('invalid')
