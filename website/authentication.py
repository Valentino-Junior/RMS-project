from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if the input is a valid email or username
        try:
            # Try to get the user by username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # If not found by username, try by email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None  # Return None if no user is found by either email or username

        # Verify the password
        if user.check_password(password):
            return user  # Return the user object if authentication succeeds
        return None  # Return None if password is incorrect