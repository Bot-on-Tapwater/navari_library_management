from django.db import models
# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password

import uuid

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, null=False, unique=True)
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    verification_token = models.UUIDField(null=True, default=uuid.uuid4, blank=True)
    password_reset_token = models.UUIDField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[('librarian', 'Librarian'), ('member', 'Member')], default='librarian')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.username
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'verification_token': str(self.verification_token) if self.verification_token else None,
            'password_reset_token': str(self.password_reset_token) if self.password_reset_token else None,
            'is_verified': self.is_verified,
            'role': self.role,
        }
