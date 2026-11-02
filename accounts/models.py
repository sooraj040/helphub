"""
Models describe what HelpHub stores in the database.
Each model becomes a table, and each field becomes a column.
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Extra information about each HelpHub user.

    Django's built-in User already stores the username, email and
    password (safely scrambled). A Profile adds the HelpHub details:
    whether the person is a customer or a worker, their phone number
    and their location.
    """

    # The two kinds of HelpHub account.
    # Left: what is saved in the database. Right: what people see.
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    ]

    # Which user this profile belongs to. Each user has one profile.
    # If a user is deleted, their profile is deleted too.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Customer or worker. This decides which dashboard they see.
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    # Optional contact details. "blank=True" means they can be left empty.
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        # How a profile is named in the admin site, e.g. "apsa - Customer".
        return f"{self.user.username} - {self.get_role_display()}"
