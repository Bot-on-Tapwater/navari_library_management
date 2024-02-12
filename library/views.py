from django.shortcuts import render
# from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.http import HttpResponseRedirect
# Create your views here.

"""EMAIL & SMTP"""
# def email(request, subject=None, message=None, from_email=None, recipient_list=None):
#     subject, message, from_email, recipient_list = ['Test Email', 'This is a test email sent using SMTP in Django.', 'brandonmunda1@gmail.com', ['mundabrandon@outlook.com']]

#     send_mail(subject, message, from_email, recipient_list)
    
#     return JsonResponse('Mail sent successfully', safe=False)

"""LANDING PAGE"""
def index_view(request):
    context = {
        'error': 'This shit dont work'
    }
    return render(request, "library/error.html", context)

"""USER AUTHENTICATION & AUTHORIZATION"""
# @require_http_methods(["POST"])
# def register_view(self, request):
#     try:
#         data = request.POST

#         username, password, email, first_name, last_name = [data['username'], data['password'], data['email'], data['first_name'], data['last_name']]

#         user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
    
#     except Exception as e:
#         return JsonResponse(e, safe=False)