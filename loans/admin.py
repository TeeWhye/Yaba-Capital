from django.contrib import admin
from .models import Borrower, LoanProduct, LoanApplication, Loan, Repayment


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone', 'created_at')
    search_fields = ('user__username', 'business_name', 'phone')


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'interest_rate',
        'min_amount',
        'max_amount',
    )
    search_fields = ('name',)


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'borrower',
        'product',
        'amount_requested',
        'status',
        'applied_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'product',
        'applied_at',
    )

    search_fields = (
        'borrower__user__username',
        'borrower__business_name',
        'product__name',
    )

    readonly_fields = (
        'applied_at',
        'updated_at',
    )

    list_editable = ('status',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'borrower',
        'principal',
        'interest_rate',
        'total_repayment',
        'due_date',
        'status',
        'disbursed_at',
    )

    list_filter = (
        'status',
        'due_date',
    )

    search_fields = (
        'borrower__business_name',
        'borrower__user__username',
    )

    admin.site.register(Repayment)