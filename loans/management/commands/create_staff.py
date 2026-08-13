from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Create the production staff account'

    def handle(self, *args, **options):
        User = get_user_model()

        username = config('STAFF_USERNAME')
        email = config('STAFF_EMAIL')
        password = config('STAFF_PASSWORD')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if not created:
            user.is_staff = True
            user.is_superuser = True
            user.email = email

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Staff account ready: {username}'
            )
        )