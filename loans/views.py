from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.views import LoginView

from .forms import SignUpForm, LoanApplicationForm, RepaymentForm
from .models import Borrower, LoanApplication, Loan

class CustomLoginView(LoginView):

    def get_success_url(self):

        if self.request.user.is_staff:
            return '/staff/'

        return '/dashboard/'

def home(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Account created. You can now apply for a loan.'
            )

            return redirect('apply')

    else:
        form = SignUpForm()

    return render(
        request,
        'registration/signup.html',
        {'form': form}
    )


@login_required
def apply_loan(request):
    if request.method == 'POST':
        form = LoanApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            application = form.save(commit=False)
            application.borrower = request.user.borrower
            application.save()

            messages.success(
                request,
                'Application submitted. We will review it shortly.'
            )

            return redirect('dashboard')

    else:
        form = LoanApplicationForm()

    return render(
        request,
        'loans/apply.html',
        {'form': form}
    )


@login_required
def dashboard(request):
    try:
        borrower = request.user.borrower

    except Borrower.DoesNotExist:
        messages.error(
            request,
            'This account is not registered as a borrower.'
        )

        return redirect('home')

    applications = LoanApplication.objects.filter(
        borrower=borrower
    )

    loans = Loan.objects.filter(
    borrower=borrower
).select_related(
    'application',
    'application__product'
).order_by(
    '-disbursed_at'
)

    active_loans = loans.filter(
    status='active'
)

    repaid_loans = loans.filter(
    status='repaid'
    )

    total_applications = applications.count()

    pending_count = applications.filter(
        status='pending'
    ).count()

    under_review_count = applications.filter(
        status='under_review'
    ).count()

    approved_count = applications.filter(
        status='approved'
    ).count()

    active_loans_count = loans.filter(
        status='active'
    ).count()

    total_outstanding = sum(
        loan.outstanding_balance
        for loan in loans.filter(status='active')
    )

    repaid_loans_count = loans.filter(
        status='repaid'
    ).count()

    return render(
        request,
        'loans/dashboard.html',
        {
            'applications': applications,
            'loans': loans,
            'active_loans': active_loans,
            'repaid_loans': repaid_loans,
            'total_applications': total_applications,
            'pending_count': pending_count,
            'under_review_count': under_review_count,
            'approved_count': approved_count,
            'active_loans_count': active_loans_count,
            'repaid_loans_count': repaid_loans_count,
            'total_outstanding': total_outstanding,
        }
    )


@login_required
def application_detail(request, application_id):
    try:
        borrower = request.user.borrower

    except Borrower.DoesNotExist:
        messages.error(
            request,
            'This account is not registered as a borrower.'
        )

        return redirect('home')

    try:
        application = LoanApplication.objects.get(
            id=application_id,
            borrower=borrower
        )

    except LoanApplication.DoesNotExist:
        messages.error(
            request,
            'Loan application not found.'
        )

        return redirect('dashboard')

    return render(
        request,
        'loans/application_detail.html',
        {'application': application}
    )


@login_required
def staff_dashboard(request):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('dashboard')

    applications = LoanApplication.objects.all()
    loans = Loan.objects.all()

    total_applications = applications.count()

    pending_count = applications.filter(
        status='pending'
    ).count()

    under_review_count = applications.filter(
        status='under_review'
    ).count()

    approved_count = applications.filter(
        status='approved'
    ).count()

    active_loans_count = loans.filter(
        status='active'
    ).count()

    repaid_loans_count = loans.filter(
        status='repaid'
    ).count()

    total_disbursed = sum(
        loan.principal
        for loan in loans.filter(
            status__in=['active', 'repaid']
        )
    )

    total_outstanding = sum(
        loan.outstanding_balance
        for loan in loans.filter(
            status='active'
        )
    )

    recent_applications = applications.order_by(
        '-applied_at'
    )[:10]

    requires_attention = applications.filter(
    status__in=['pending', 'under_review']
).order_by(
    'applied_at'
)[:10]

    return render(
        request,
        'loans/staff_dashboard.html',
        {
            'total_applications': total_applications,
            'pending_count': pending_count,
            'under_review_count': under_review_count,
            'approved_count': approved_count,
            'active_loans_count': active_loans_count,
            'repaid_loans_count': repaid_loans_count,
            'total_disbursed': total_disbursed,
            'total_outstanding': total_outstanding,
            'recent_applications': recent_applications,
            'requires_attention': requires_attention,
        }
    )
@login_required
def staff_applications(request):
    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('dashboard')

    applications = LoanApplication.objects.all()

    return render(
        request,
        'loans/staff_applications.html',
        {'applications': applications}
    )

@login_required
def staff_loans(request):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('dashboard')

    today = timezone.now().date()

    loans = Loan.objects.filter(
        status__in=['active', 'repaid']
    ).select_related(
        'borrower',
        'application',
        'application__product'
    ).order_by(
        'due_date'
    )

    for loan in loans:

        # -----------------------------
        # LOAN STATE
        # -----------------------------

        if loan.status == 'repaid':

            loan.loan_state = 'repaid'
            loan.days_difference = 0

        else:

            loan.days_difference = (
                loan.due_date - today
            ).days

            if loan.days_difference < 0:

                loan.loan_state = 'overdue'

            elif loan.days_difference <= 7:

                loan.loan_state = 'due_soon'

            else:

                loan.loan_state = 'active'

        # -----------------------------
        # REPAYMENT PERCENTAGE
        # -----------------------------

        if loan.status == 'repaid':

            loan.repayment_percentage = 100

        elif loan.total_repayment > 0:

            loan.repayment_percentage = (
                loan.total_paid
                / loan.total_repayment
            ) * 100

        else:

            loan.repayment_percentage = 0

    return render(
        request,
        'loans/staff_loans.html',
        {
            'loans': loans,
        }
    )


@login_required
def staff_application_detail(request, application_id):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('dashboard')

    try:
        application = LoanApplication.objects.get(
            id=application_id
        )

    except LoanApplication.DoesNotExist:
        messages.error(
            request,
            'Loan application not found.'
        )

        return redirect('staff_applications')

    if request.method == 'POST':

        action = request.POST.get('action')

        reviewer_note = request.POST.get(
            'reviewer_note',
            ''
        ).strip()

        # --------------------------------
        # MARK UNDER REVIEW
        # --------------------------------

        if action == 'under_review':

            if application.status != 'pending':
                messages.error(
                    request,
                    'Only pending applications can be marked under review.'
                )

            else:
                application.status = 'under_review'
                application.save()

                messages.success(
                    request,
                    'Application marked as under review.'
                )

        # --------------------------------
        # APPROVE APPLICATION
        # --------------------------------

        elif action == 'approved':

            if application.status != 'under_review':
                messages.error(
                    request,
                    'Only applications under review can be approved.'
                )

            else:

                application.status = 'approved'
                application.reviewer_note = reviewer_note
                application.save()

                # Check whether a loan already exists
                try:
                    application.loan

                    messages.warning(
                        request,
                        'A loan already exists for this application.'
                    )

                except Loan.DoesNotExist:

                    Loan.objects.create(
                        application=application,
                        borrower=application.borrower,
                        principal=application.amount_requested,
                        interest_rate=application.product.interest_rate,
                        total_repayment=(
                            application.amount_requested
                            + (
                                application.amount_requested
                                * application.product.interest_rate
                                / 100
                            )
                        ),
                        due_date=(
                            timezone.now().date()
                            + timezone.timedelta(
                                days=application.product.repayment_period
                            )
                        ),
                        status='approved'
                    )

                    messages.success(
                        request,
                        'Application approved and loan created successfully.'
                    )

        # --------------------------------
        # DISBURSE LOAN
        # --------------------------------

        elif action == 'disbursed':

            if application.status != 'approved':
                messages.error(
                    request,
                    'Only approved applications can be disbursed.'
                )

            else:

                try:
                    loan = application.loan

                except Loan.DoesNotExist:

                    messages.error(
                        request,
                        'No loan exists for this application.'
                    )

                    return redirect(
                        'staff_application_detail',
                        application_id=application.id
                    )

                if loan.status != 'approved':
                    messages.error(
                        request,
                        'This loan has already been disbursed or is no longer available for disbursement.'
                    )

                else:

                    disbursement_time = timezone.now()

                    loan.disbursed_at = disbursement_time

                    loan.due_date = (
                        disbursement_time.date()
                        + timezone.timedelta(
                            days=application.product.repayment_period
                        )
                    )

                    loan.status = 'active'
                    loan.save()

                    application.status = 'active'
                    application.save()

                    messages.success(
                        request,
                        'Loan marked as disbursed and is now active.'
                    )

        # --------------------------------
        # REJECT APPLICATION
        # --------------------------------

        elif action == 'rejected':

            if application.status != 'under_review':
                messages.error(
                    request,
                    'Only applications under review can be rejected.'
                )

            else:

                application.status = 'rejected'
                application.reviewer_note = reviewer_note
                application.save()

                messages.success(
                    request,
                    'Application rejected.'
                )

        # --------------------------------
        # UNKNOWN ACTION
        # --------------------------------

        else:

            messages.error(
                request,
                'Invalid application action.'
            )

        return redirect(
            'staff_application_detail',
            application_id=application.id
        )

    return render(
        request,
        'loans/staff_application_detail.html',
        {'application': application}
    )

@login_required
def record_repayment(request, loan_id):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to record repayments.'
        )

        return redirect('dashboard')

    try:
        loan = Loan.objects.get(
            id=loan_id
        )

    except Loan.DoesNotExist:
        messages.error(
            request,
            'Loan not found.'
        )

        return redirect('staff_applications')

    if loan.status != 'active':
        messages.error(
            request,
            'Repayments can only be recorded for active loans.'
        )

        return redirect(
            'staff_application_detail',
            application_id=loan.application.id
        )

    if request.method == 'POST':

        form = RepaymentForm(
            request.POST,
            loan=loan
        )

        if form.is_valid():

            with transaction.atomic():

                loan = Loan.objects.select_for_update().get(
                    id=loan.id
                )

                # Re-check the loan status after locking it
                if loan.status != 'active':

                    messages.error(
                        request,
                        'This loan is no longer active.'
                    )

                    return redirect(
                        'staff_application_detail',
                        application_id=loan.application.id
                    )

                # Re-check the repayment amount against
                # the latest outstanding balance
                amount = form.cleaned_data['amount']

                if amount > loan.outstanding_balance:

                    form.add_error(
                        'amount',
                        f'Repayment cannot exceed the outstanding '
                        f'balance of ₦{loan.outstanding_balance:.2f}.'
                    )

                else:

                    repayment = form.save(commit=False)
                    repayment.loan = loan
                    repayment.save()

                    if loan.outstanding_balance <= 0:

                        loan.status = 'repaid'
                        loan.save()

                        loan.application.status = 'repaid'
                        loan.application.save()

                    messages.success(
                        request,
                        'Repayment recorded successfully.'
                    )

                    return redirect(
                        'staff_application_detail',
                        application_id=loan.application.id
                    )

    else:

        form = RepaymentForm(
            loan=loan
        )

    return render(
        request,
        'loans/record_repayment.html',
        {
            'form': form,
            'loan': loan,
        }
    )