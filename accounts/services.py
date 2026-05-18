from django.contrib.auth.models import User
from django.db import transaction


def create_account(*, username, email, first_name, last_name, password):
    """
    Creates a User atomically.
    Returns the newly created User on success.
    """
    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        return user
