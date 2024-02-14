from django.shortcuts import render
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserForm
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.

"""EMAIL & SMTP"""
def email(subject=None, message=None, from_email=None, recipient_list=None):
    # subject, message, from_email, recipient_list = ['Test Email', 'This is a test email sent using SMTP in Django.', 'brandonmunda1@gmail.com', ['mundabrandon@outlook.com']]
    from_email = 'brandonmunda1@gmail.com'

    send_mail(subject, message, from_email, recipient_list)
    
    return JsonResponse('Mail sent successfully', safe=False)

"""LANDING PAGE"""
def index_view(request):
    context = {
        'error': 'This shit dont work'
    }
    return render(request, "library/error.html", context)

"""USER AUTHENTICATION & AUTHORIZATION"""
@require_http_methods(["POST", "GET"])
def register_view(request):
    if request.method == 'POST':
        try:
            form = UserForm(request.POST)

            if form.is_valid():

                username, password, email, first_name, last_name, role = [form.cleaned_data['username'], form.cleaned_data['password'], form.cleaned_data['email'], form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['role']]

                new_user = User(username=username, password=make_password(password), email=email, first_name=first_name, last_name=last_name, role=role)

                new_user.save()

                send_registration_mail(new_user)
            
            return JsonResponse(new_user.to_dict(), safe=False)                
        
        except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)
    
    else:
        form = UserForm()
    
    return render(request, 'library/register.html', {'form': form})

def send_registration_mail(new_user):
    verification_link = f"http://0.0.0.0:8000/library/verify-email/?token={new_user.verification_token}"

    subject = "Navari Library - Verify your email address"

    recipient_list = [new_user.email]

    message = f"Please click on the following link to verify your email address: {verification_link}"

    email(subject=subject, recipient_list=recipient_list, message=message)

def verify_email(request):
    if 'token' in request.GET:
        verification_token = request.GET['token']
        try:
            user = User.objects.get(verification_token=verification_token)

            user.is_verified = True

            user.save()

            return render(request, 'library/verification-success.html', {'user': user, 'user_dict': user.to_dict()})
        
        except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["POST", "GET"])
def login_view(request):
    if request.method == "POST":
        try:
            data = request.POST

            email, password = [data['email'], data['password']]

            user = User.objects.get(email=email)

            if check_password(password, user.password):
                return JsonResponse(user.to_dict(), safe=False)

        except Exception as e:
                print(e)
                context = {
                    'error': str(e)
                }
                return render(request, "library/error.html", context)

    else:
        return render(request, "library/login.html")

