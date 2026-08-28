import requests
from django.conf import settings


PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_payment(
    email,
    amount,
    reference,
    callback_url,
    metadata=None,
):
    """
    Initialize a Paystack transaction.

    Paystack expects the amount in kobo.
    For example:
    ₦1,000 = 100000 kobo
    """

    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": email,
        "amount": int(amount * 100),
        "reference": reference,
        "callback_url": callback_url,
    }

    if metadata:
        data["metadata"] = metadata

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def verify_payment(reference):
    """
    Verify a Paystack transaction using its reference.
    """

    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()