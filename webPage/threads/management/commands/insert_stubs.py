"""
    This module is a script to insert two magazine objects in the database
"""

from django.core.management.base import BaseCommand
from threads.models import Magazine, User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    """
    Insert two magazine objects in the database
    """

    help = "Insert Stubs"

    def handle(self, *args, **kwargs):
        Magazine.objects.create(name="random")  # pylint: disable=no-member
        Magazine.objects.create(name="openSource")  # pylint: disable=no-member
        User.objects.create(  # pylint: disable=no-member
            username="admin", email="admin@gmail.com"
        )
        user = User.objects.create(  # pylint: disable=no-member
            username="chen", email="chen@gmail.com"
        )
        Token.objects.create(user=user)

        self.stdout.write(
            self.style.SUCCESS(  # pylint: disable=no-member
                "Two magazine objects and Two user object inserted in the database successfully."
            )
        )
