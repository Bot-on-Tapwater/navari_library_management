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
import datetime
from django.contrib.postgres.search import SearchVector
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

def outstanding_balance(view_func):
     @wraps(view_func)
     def wrapper(request, *args, **kwargs):
          calculate_overdue_charges_and_member_balance()
          return view_func(request, *args, **kwargs)
     return wrapper

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
@require_http_methods(["GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
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

@require_http_methods(["GET"])
@role_required('librarian')
@csrf_exempt
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

@require_http_methods(["POST", "GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
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

@require_http_methods(["PUT", "GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def update_new_member(request, member_id):
    try:
        member_to_update = Member.objects.get(pk=member_id)

        for field, value in QueryDict(request.body).items():
            if (hasattr(member_to_update, field)):
                setattr(member_to_update, field, value)
        
        member_to_update.save()

        return JsonResponse(member_to_update.to_dict(), safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["DELETE"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def delete_member(request, member_id):
    try:
         member_to_delete = Member.objects.get(pk=member_id)

         member_to_delete.delete()

         return JsonResponse({"message": "Member deleted successfully"}, safe=False)
    
    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

"""TRANSACTIONS"""
@require_http_methods(["POST", "GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def issue_book(request, member_id, book_id):
     try:
          member = Member.objects.get(pk=member_id)

          if member.debt_limit_reached:
               return JsonResponse({"message": "Member outstanding debt exceeded library limits!"})

          book = Book.objects.get(pk=book_id)

          issue_date = datetime.date.today()

          new_transaction = Transaction(member=member, book=book, issue_date=issue_date)

          new_transaction.save()

          book.quantity -= 1

          book.save()

          return JsonResponse(new_transaction.to_dict(), safe=False)
     
     except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["PUT", "GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def return_book(request, transaction_id):     
     try:
          transaction = Transaction.objects.get(pk=transaction_id)

          member = transaction.member

          book = transaction.book

          return_date = datetime.date.today()

          transaction.return_date = return_date

          transaction.save()

          book.quantity += 1

          book.save()

          member.fee_balance = sum([transaction.fee for transaction in Transaction.objects.filter(member=member)])

          member.save()          

          return JsonResponse(transaction.to_dict(), safe=False)
     
     except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["DELETE", "PUT"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def clear_fee_for_book(request, transaction_id):
     try:
          transaction = Transaction.objects.get(pk=transaction_id)

          member = transaction.member

          book = transaction.book

          member.fee_balance = sum([transaction.fee for transaction in Transaction.objects.filter(member=member)])

          member.save()

          transaction.delete()

          return JsonResponse(member.to_dict(), safe=False)
     
     except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["DELETE", "PUT"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def clear_member_outstanding_balance(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)

        [transaction.delete() for transaction in  Transaction.objects.filter(member=member)]

        member.fee_balance = sum([transaction.fee for transaction in Transaction.objects.filter(member=member)])

        member.save()

        return JsonResponse(member.to_dict(), safe=False)
    
    except Exception as e:
        print(e)
        context = {
            'error': str(e)
        }
        return render(request, "library/error.html", context)

@require_http_methods(["GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def list_all_transactions(request):
    try:
        all_transactions = Transaction.objects.all()

        return JsonResponse([transaction.to_dict() for transaction in all_transactions], safe=False)

    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["GET"])
@role_required('librarian')
@csrf_exempt
@outstanding_balance
def transaction_with_transaction_id(request, transaction_id):
     try:
          transaction = Transaction.objects.get(pk=transaction_id)

          return JsonResponse(transaction.to_dict(), safe=False)
     
     except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

def calculate_overdue_charges_and_member_balance():
        all_members = Member.objects.all()

        for member in all_members:
            all_transactions = Transaction.objects.filter(member=member)

        for transaction in all_transactions:
            days_borrowed = (datetime.date.today() - transaction.issue_date).days

            if (days_borrowed > 14):
                transaction.fee = 20 + ((days_borrowed - 14) * 10) # Default 20 KES for borrowing book plus 10 KES/day overdue charge after 14 days
                transaction.save()
        
        fee_balance = sum([transaction.fee for transaction in all_transactions])
        
        member.debt_limit_reached = True if fee_balance >= 500 else False
        
        member.fee_balance = fee_balance

        member.save()

"""SEARCH"""
@require_http_methods(["GET"])
@outstanding_balance
def search_for_book(request):
    try:
        search = request.GET.get('search')

        search_vector = SearchVector('title', 'author', 'description')

        books = Book.objects.annotate(search=search_vector).filter(search=search)

        return JsonResponse([book.to_dict() for book in books], safe=False)

    except Exception as e:
            print(e)
            context = {
                'error': str(e)
            }
            return render(request, "library/error.html", context)

@require_http_methods(["GET"])
@role_required('librarian')
@outstanding_balance
def search_for_member(request):
    try:
        search = request.GET.get('search')

        search_vector = SearchVector('email', 'name')

        members = Member.objects.annotate(search=search_vector).filter(search=search)

        return JsonResponse([member.to_dict() for member in members], safe=False)

    except Exception as e:
                print(e)
                context = {
                    'error': str(e)
                }
                return render(request, "library/error.html", context)