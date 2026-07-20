import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    """Extra per-user data not covered by Django's built-in User model.

    The admin/user distinction is carried by ``User.is_staff`` (True = admin),
    so it is intentionally not duplicated here.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile<{self.user.email}>'


class OTPCodeManager(models.Manager):
    def create_for_user(self, user):
        """Invalidate any outstanding codes and issue a fresh one.

        Returns a tuple of ``(otp_instance, raw_code)``. The raw code is only
        available here (it is stored hashed) and must be emailed immediately.
        """
        self.filter(user=user, used=False).update(used=True)

        length = getattr(settings, 'OTP_CODE_LENGTH', 6)
        raw_code = ''.join(secrets.choice('0123456789') for _ in range(length))
        expires_at = timezone.now() + timezone.timedelta(
            minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
        )
        otp = self.create(
            user=user,
            code=make_password(raw_code),
            expires_at=expires_at,
        )
        return otp, raw_code


class OTPCode(models.Model):
    """A single-use, time-limited login code delivered by email."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='otp_codes'
    )
    code = models.CharField(max_length=128)  # hashed
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    objects = OTPCodeManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'used']),
        ]

    def __str__(self):
        return f'OTP<{self.user.email} used={self.used}>'

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def verify(self, raw_code):
        """Return True if ``raw_code`` matches and the code is still valid."""
        return self.is_valid() and check_password(raw_code, self.code)
