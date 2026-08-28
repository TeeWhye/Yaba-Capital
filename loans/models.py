from django.db import models
from django.contrib.auth.models import User


class Borrower(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='borrower'
    )
    phone = models.CharField(max_length=20)
    business_name = models.CharField(max_length=200)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.business_name} ({self.user.username})'


class LoanProduct(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Flat rate per cycle, e.g. 5.00 for 5%'
    )

    min_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    max_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    repayment_period = models.PositiveIntegerField(
        default=30,
        help_text='Repayment period in days'
    )

    def __str__(self):
        return self.name


class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('repaid', 'Repaid'),
    ]

    borrower = models.ForeignKey(
        Borrower,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT
    )

    amount_requested = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    purpose = models.TextField()

    # Bank details for loan disbursement
    bank_name = models.CharField(
    max_length=100,
    blank=True,
    null=True
)

    account_name = models.CharField(
    max_length=200,
    blank=True,
    null=True
)

    account_number = models.CharField(
    max_length=10,
    blank=True,
    null=True
    )

    nin_document = models.FileField(
    upload_to='nin_documents/',
    blank=True,
    null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reviewer_note = models.TextField(
        blank=True
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.borrower} - {self.product} - {self.status}'

class Loan(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('repaid', 'Repaid'),
    ]

    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name='loan'
    )

    borrower = models.ForeignKey(
        Borrower,
        on_delete=models.PROTECT,
        related_name='loans'
    )

    principal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    total_repayment = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    disbursed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    @property
    def total_paid(self):
        return sum(
            repayment.amount
            for repayment in self.repayments.filter(
                status='confirmed'
            )
        )

    @property
    def outstanding_balance(self):
        return self.total_repayment - self.total_paid

    def __str__(self):
        return f'{self.borrower} - ₦{self.principal} - {self.status}'


class Repayment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]

    loan = models.ForeignKey(
        Loan,
        on_delete=models.PROTECT,
        related_name='repayments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    paystack_reference = models.CharField(
    max_length=100,
    unique=True,
    null=True,
    blank=True
)

    paid_at = models.DateTimeField(
        auto_now_add=True
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    note = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f'{self.loan.borrower} - '
            f'₦{self.amount} - '
            f'{self.get_status_display()}'
        )