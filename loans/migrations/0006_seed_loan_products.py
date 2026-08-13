from django.db import migrations


def create_loan_products(apps, schema_editor):
    LoanProduct = apps.get_model('loans', 'LoanProduct')

    LoanProduct.objects.get_or_create(
        name='Working Capital Loan',
        defaults={
            'description': 'Short-term financing for business working capital.',
            'interest_rate': 5.00,
            'min_amount': 50000.00,
            'max_amount': 1000000.00,
            'repayment_period': 30,
        },
    )

    LoanProduct.objects.get_or_create(
        name='Starter business loan',
        defaults={
            'description': 'Starter pack',
            'interest_rate': 5.00,
            'min_amount': 100000.00,
            'max_amount': 150000.00,
            'repayment_period': 30,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_loanproduct_repayment_period'),
    ]

    operations = [
        migrations.RunPython(create_loan_products),
    ]