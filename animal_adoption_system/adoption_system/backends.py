from django.contrib.auth.models import User
from .models import Profile

class EmailOrPhoneBackend:
    def authenticate(self, request, username=None, password=None):
        user = None

        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass

        if not user:
            try:
                profile = Profile.objects.get(phone_number=username)
                user = profile.user
            except Profile.DoesNotExist:
                return None

        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
