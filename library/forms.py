from django import forms

class UserForm(forms.Form):
    ROLES = [
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    username = forms.CharField(max_length=100, label='Username', required=False)
    email = forms.EmailField(label='Email', required=False)
    password = forms.CharField(max_length=100, label='Password', widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(max_length=100, label='First Name', required=False)
    last_name = forms.CharField(max_length=100, label='Last Name', required=False)
    # verification_token = forms.UUIDField(required=False, label='Verification Token')
    # password_reset_token = forms.UUIDField(required=False, label='Password Reset Token')
    # is_verified = forms.BooleanField(required=False, initial=False, label='Is Verified')
    role = forms.ChoiceField(choices=ROLES, label='Role', initial='librarian')