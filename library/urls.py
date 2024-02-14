from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    # Email
    # path('email', views.email, name='email'),
    # Landing page
    path('', views.index_view, name='index'),
    # User Authentication & Authorization
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('login/', views.login_view, name="login"),
    path('request-password-reset/', views.request_password_reset, name="request-password-reset"),
    path('validate-password-reset-token/', views.validate_passsword_reset_token),
    path('reset-password/', views.reset_password, name="reset-password"),
    path('logout/', views.logout_view, name='logout')
]