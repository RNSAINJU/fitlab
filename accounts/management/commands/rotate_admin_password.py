from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.security import get_admin_password_from_env, is_weak_password

User = get_user_model()


class Command(BaseCommand):
    help = "Set the admin password from FITLAB_ADMIN_PASSWORD in the environment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="admin@fitlab.com",
            help="Admin account email to update",
        )

    def handle(self, *args, **options):
        password = get_admin_password_from_env()
        if not password:
            raise CommandError("FITLAB_ADMIN_PASSWORD is not set in the environment.")

        if is_weak_password(password):
            raise CommandError(
                "FITLAB_ADMIN_PASSWORD is too weak. Use at least 12 characters "
                "and avoid common defaults like admin123."
            )

        email = options["email"].lower()
        admin = User.objects.filter(email__iexact=email, is_staff=True).first()
        if admin is None:
            raise CommandError(f"No staff user found for {email}.")

        admin.set_password(password)
        admin.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS(f"Updated password for {email}."))
