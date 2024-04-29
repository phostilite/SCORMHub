from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Creates an admin user.'  # Descriptive help text

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)  # Add other arguments if needed (email, etc.)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = 'Priuu@@##68'  

        if not CustomUser.objects.filter(username=username).exists():
            admin_user = CustomUser.objects.create_user(
                username=username,
                password=password, 
                is_core_admin=True
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'Username "{username}" already exists'))
