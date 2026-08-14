from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('apply/', views.apply_loan, name='apply'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'application/<int:application_id>/',
        views.application_detail,
        name='application_detail'
    ),

path(
    'staff/',
    views.staff_dashboard,
    name='staff_dashboard'
),
path(
    'staff/applications/',
    views.staff_applications,
    name='staff_applications'
),
path(
    'staff/loans/',
    views.staff_loans,
    name='staff_loans'
),

path(
    'staff/applications/<int:application_id>/',
    views.staff_application_detail,
    name='staff_application_detail'
),

path(
    'loan/<int:loan_id>/repay/',
    views.record_repayment,
    name='record_repayment'
),

path(
    'my-loan/<int:loan_id>/repay/',
    views.borrower_repayment,
    name='borrower_repayment'
),
]