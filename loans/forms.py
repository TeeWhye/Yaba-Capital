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

    bank_name = forms.CharField(
        required=True,
        label='Bank name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your bank name',
            }
        )
    )

    account_name = forms.CharField(
        required=True,
        label='Account name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter the account name',
            }
        )
    )

    account_number = forms.CharField(
        required=True,
        label='Account number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your 10-digit account number',
                'inputmode': 'numeric',
                'maxlength': '10',
            }
        )
    )

    nin_document = forms.FileField(
        required=True,
        label='NIN document',
        widget=forms.FileInput(
            attrs={
                'accept': '.pdf,.jpg,.jpeg,.png',
            }
        ),
        help_text=(
            'Upload a clear copy of your NIN document. '
            'Accepted formats: PDF, JPG, JPEG or PNG.'
        )
    )

    class Meta:
        model = LoanApplication
        fields = [
            'product',
            'amount_requested',
            'purpose',
            'bank_name',
            'account_name',
            'account_number',
            'nin_document',
        ]

        def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)

        # Show each product's loan range in the product dropdown
         self.fields['product'].label_from_instance = (
            lambda product:
            f'{product.name} '
            f'(₦{product.min_amount:,.2f} - '
            f'₦{product.max_amount:,.2f})'
        )

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

    def clean_account_number(self):

        account_number = self.cleaned_data.get(
            'account_number'
        )

        if not account_number:
            raise forms.ValidationError(
                'Account number is required.'
            )

        if not account_number.isdigit():
            raise forms.ValidationError(
                'Account number must contain only numbers.'
            )

        if len(account_number) != 10:
            raise forms.ValidationError(
                'Account number must be exactly 10 digits.'
            )

        return account_number

    def clean_nin_document(self):

        nin_document = self.cleaned_data.get(
            'nin_document'
        )

        if not nin_document:
            raise forms.ValidationError(
                'NIN document is required.'
            )

        allowed_extensions = [
            '.pdf',
            '.jpg',
            '.jpeg',
            '.png',
        ]

        filename = nin_document.name.lower()

        if not any(
            filename.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                'Please upload a valid NIN document '
                'in PDF, JPG, JPEG or PNG format.'
            )

        return nin_document


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