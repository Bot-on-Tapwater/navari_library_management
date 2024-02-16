from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    # Landing page
    path('', views.index_view, name='index'),

    # User Authentication & Authorization
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('login/', views.login_view, name="login"),
    path('request-password-reset/', views.request_password_reset, name="request-password-reset"),
    path('validate-password-reset-token/', views.validate_passsword_reset_token),
    path('reset-password/', views.reset_password, name="reset-password"),
    path('logout/', views.logout_view, name='logout'),

    # Books
    path('books/', views.list_all_books, name='books'),
    path('books/<int:book_id>/', views.book_with_specific_id, name="specific-book"),
    path('books/create/', views.create_new_book, name="create-book"),
    path('books/update/<int:book_id>/', views.update_book, name="update-book"),
    path('books/delete/<int:book_id>/', views.delete_book, name="delete-book"),

    # Members
    path('members/', views.list_all_members, name='members'),
    path('members/<int:member_id>/', views.member_with_specific_id, name='specific-member'),
    path('members/create/', views.create_new_member, name="create-member"),
    path('members/update/<int:member_id>/', views.update_new_member, name="update-member"),
    path('members/delete/<int:member_id>/', views.delete_member, name="delete-member"),

    # Transactions
    path('members/<int:member_id>/books/<int:book_id>/issue/', views.issue_book, name='issue-book'),
    path('transactions/<int:transaction_id>/return/', views.return_book, name='return-book'),
    path('transactions/<int:transaction_id>/clear-fee/', views.clear_fee_for_book, name='clear-fee'),
    path('members/<int:member_id>/clear-balance/', views.clear_member_outstanding_balance, name='clear-balance'),
    path('transactions/', views.list_all_transactions, name='transactions'),
    path('transactions/<int:transaction_id>/', views.transaction_with_transaction_id, name='specific-transaction'),

    # Search
    path('search/members/', views.search_for_member, name='search-member'),
    path('search/books/', views.search_for_book, name='search-book'),

]