from django.db import models
# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MaxValueValidator
import uuid
from django.db.models import CheckConstraint, Q
from datetime import timedelta

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

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'quantity': self.quantity,
        }

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    debt_limit_reached = models.BooleanField(default=False)
    fee_balance = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(500)])

    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'email': self.email,
            'debt_limit_reached': self.debt_limit_reached,
            'fee_balance': self.fee_balance,
        }

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fee = models.PositiveIntegerField(default=20) # 20KES for renting book for 14 days

    def __str__(self):
        return f"{self.book} - {self.member}"
    
    def to_dict(self):
        return {
            'id': self.pk,
            'book': self.book.to_dict(),
            'member': self.member.to_dict(),
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'fee': self.fee,
        }