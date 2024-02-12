from django import forms

class UserForm(forms.Form):
    ROLES = [
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    username = forms.CharField(max_length=100, label='Username')
    email = forms.EmailField(label='Email')
    password = forms.CharField(max_length=100, label='Password', widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100, label='First Name')
    last_name = forms.CharField(max_length=100, label='Last Name')
    verification_token = forms.UUIDField(required=False, label='Verification Token')
    password_reset_token = forms.UUIDField(required=False, label='Password Reset Token')
    is_verified = forms.BooleanField(required=False, initial=False, label='Is Verified')
    role = forms.ChoiceField(choices=ROLES, label='Role', initial='librarian')