from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from accounts.security import get_admin_password_from_env, is_weak_password, production_security_enabled
from loyalty.models import PointTransaction
from loyalty.rule_engine import ensure_default_point_rules
from loyalty.services import award_points
from rewards.models import Reward

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo admin user, sample rewards, and optional test customer"

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@fitlab.com")
        parser.add_argument("--admin-password", default="")
        parser.add_argument("--with-customer", action="store_true")

    def handle(self, *args, **options):
        admin_email = options["admin_email"].lower()
        admin_password = options["admin_password"] or get_admin_password_from_env()

        if production_security_enabled():
            if not admin_password:
                raise CommandError(
                    "FITLAB_ADMIN_PASSWORD must be set in production before running setup_fitlab."
                )
            if is_weak_password(admin_password):
                raise CommandError(
                    "FITLAB_ADMIN_PASSWORD is too weak for production. "
                    "Use at least 12 characters."
                )
        elif not admin_password:
            admin_password = "admin123"
            self.stdout.write(
                self.style.WARNING(
                    "Using development-only default admin password. "
                    "Set FITLAB_ADMIN_PASSWORD for production."
                )
            )

        ensure_default_point_rules()

        admin, created = User.objects.get_or_create(
            username=admin_email,
            defaults={
                "email": admin_email,
                "first_name": "Fitlab",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
                "approval_status": User.ApprovalStatus.APPROVED,
            },
        )
        if created:
            admin.set_password(admin_password)
            admin.save()
            if production_security_enabled():
                self.stdout.write(self.style.SUCCESS(f"Created admin: {admin_email}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Created admin: {admin_email} / {admin_password}"))
        else:
            self.stdout.write(f"Admin already exists: {admin_email}")

        rewards_data = [
            ("Free protein shake", "Redeem at the front desk", 250, "🥤"),
            ("Guest pass", "Bring a friend for one session", 500, "🎟️"),
            ("Fitlab tee", "Branded gym t-shirt", 800, "👕"),
            ("1 month upgrade", "Premium membership upgrade", 1500, "⭐"),
        ]
        for title, desc, cost, emoji in rewards_data:
            Reward.objects.get_or_create(
                title=title,
                defaults={
                    "description": desc,
                    "points_cost": cost,
                    "image_emoji": emoji,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Sample rewards ready"))

        if options["with_customer"]:
            if production_security_enabled():
                self.stdout.write(
                    self.style.WARNING(
                        "Skipping demo customer creation in production. "
                        "Use --with-customer only for local development."
                    )
                )
                return

            email = "customer@fitlab.com"
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": "Demo",
                    "last_name": "Customer",
                    "approval_status": User.ApprovalStatus.APPROVED,
                },
            )
            if created:
                user.set_password("customer123")
                user.save()
                award_points(
                    user,
                    1000,
                    PointTransaction.TransactionType.EARN,
                    "Welcome bonus",
                )
                self.stdout.write(self.style.SUCCESS(f"Created customer: {email} / customer123"))
            else:
                self.stdout.write(f"Customer already exists: {email}")
