from django.shortcuts import render
from .models import User, Book, Transaction, Member
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse, QueryDict
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from .forms import UserForm
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
import uuid
from django.contrib.sessions.models import Session
from functools import wraps
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

"""DECORATORS"""
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'user_role' not in request.session or request.session['user_role'] != role:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

"""EMAIL & SMTP"""
def send_email(subject=None, message=None, from_email=None, recipient_list=None):
    from_email = 'brandonmunda1@gmail.com'

    send_mail(subject, message, from_email, recipient_list)
    
    return JsonResponse('Mail sent successfully', safe=False)

"""LANDING PAGE"""
def index_view(request):
    return render(request, "library/index.html")

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

    send_email(subject=subject, recipient_list=recipient_list, message=message)

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
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = request.POST

            email, password = [data['email'], data['password']]

            user = User.objects.get(email=email)

            if check_password(password, user.password):
                request.session['user_id'] = str(user.id)
                request.session['user_role'] = user.role
                return render(request, "library/index.html")

        except Exception as e:
                print(e)
                context = {
                    'error': str(e)
                }
                return render(request, "library/error.html", context)

    else:
        return render(request, "library/login.html")

@require_http_methods(["POST", "GET"])
def request_password_reset(request):
    if request.method == "POST":
        try:
            email = request.POST['email']

            user = User.objects.get(email=email)

            user.password_reset_token = uuid.uuid4()

            user.save()

            reset_link = f"http://0.0.0.0:8000/library/validate-password-reset-token/?token={user.password_reset_token}"

            subject = "Password Reset Request"

            message = f"Click the link below to reset your password:\n{reset_link}"

            # Send the password reset email
            send_email(subject=subject, message=message, recipient_list=[user.email])

            return JsonResponse({'message': 'Password reset email sent successfully'})

        except User.DoesNotExist:
            return JsonResponse({'error': 'User with this email does not exist'})

    else:
        return render(request, 'library/password_reset_request.html')

@require_http_methods(["GET"])
def validate_passsword_reset_token(request):
    if 'token' in request.GET:
        password_reset_token = request.GET['token']
        try:
            user = User.objects.get(password_reset_token=password_reset_token)

            return render(request, 'library/password_reset.html', {'user': user})
        
        except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

def reset_password(request):
    try:
        password = request.POST['password']

        email = request.POST['email']

        user = User.objects.get(email=email)

        user.set_password(password)

        user.save()

        return JsonResponse({'message': "Password reset successfully"}, safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)
    
def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['user_role']
        return render(request, "library/index.html")

"""BOOKS"""
@require_http_methods(["GET"])
@login_required
def list_all_books(request):
    try:
        all_books = Book.objects.all()

        return JsonResponse([book.to_dict() for book in all_books], safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["GET"])
@login_required
def book_with_specific_id(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)

        return JsonResponse(book.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["POST", "GET"])
@role_required('librarian')
@csrf_exempt
def create_new_book(request):
    try:
        data = request.POST

        title, author, description, quantity = [data['title'], data['author'], data['description'], data['quantity']]

        new_book = Book(title=title, author=author, description=description, quantity=quantity)

        new_book.save()

        return JsonResponse(new_book.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["PUT", "GET"])
@role_required('librarian')
@csrf_exempt
def update_book(request, book_id):
    try:
        book_to_update = Book.objects.get(pk=book_id)

        for field, value in QueryDict(request.body).items():
            if (hasattr(book_to_update, field)):
                setattr(book_to_update, field, value)
        
        book_to_update.save()
        
        return JsonResponse(book_to_update.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["DELETE"])
@role_required('librarian')
@csrf_exempt
def delete_book(request, book_id):
    try:
        book_to_delete = Book.objects.get(pk=book_id)

        book_to_delete.delete()

        return JsonResponse({"message": "Book deleted successfully"}, safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

"""MEMBERS"""
def list_all_members(request):
    try:
        all_members = Member.objects.all()

        return JsonResponse([member.to_dict() for member in all_members], safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

def member_with_specific_id(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)

        return JsonResponse(member.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

def create_new_member(request):
    try:
        data = request.POST

        name, email = [data['name'], data['email']]

        new_member = Member(name=name, email=email)

        new_member.save()

        return JsonResponse(new_member.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)