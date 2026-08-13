from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Borrower, LoanApplication, Repayment


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20)
    business_name = forms.CharField(max_length=200)
    address = forms.CharField(
        widget=forms.Textarea
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            Borrower.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                business_name=self.cleaned_data['business_name'],
                address=self.cleaned_data['address'],
            )

        return user


class LoanApplicationForm(forms.ModelForm):

    class Meta:
        model = LoanApplication
        fields = [
            'product',
            'amount_requested',
            'purpose',
            'id_document'
        ]

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get('product')
        amount = cleaned_data.get('amount_requested')

        if product and amount:
            if (
                amount < product.min_amount
                or amount > product.max_amount
            ):
                raise forms.ValidationError(
                    f'Amount must be between '
                    f'{product.min_amount} and '
                    f'{product.max_amount} for '
                    f'{product.name}.'
                )

        return cleaned_data


class RepaymentForm(forms.ModelForm):

    class Meta:
        model = Repayment
        fields = [
            'amount',
            'note',
        ]

        widgets = {
            'amount': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter repayment amount',
                    'step': '0.01',
                    'min': '0.01',
                }
            ),
            'note': forms.Textarea(
                attrs={
                    'placeholder': 'Optional repayment note',
                    'rows': 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount is None:
            return amount

        if amount <= 0:
            raise forms.ValidationError(
                'Repayment amount must be greater than zero.'
            )

        if self.loan and amount > self.loan.outstanding_balance:
            raise forms.ValidationError(
                f'Repayment cannot exceed the outstanding balance '
                f'of ₦{self.loan.outstanding_balance:.2f}.'
            )

        return amount