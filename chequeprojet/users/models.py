from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class UserAccount(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("blocked", "Blocked"),
        ("activated", "activated"),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)  # store hashed
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="waiting"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
