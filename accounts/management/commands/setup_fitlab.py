from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from loyalty.models import PointTransaction
from loyalty.rule_engine import ensure_default_point_rules
from loyalty.services import award_points
from rewards.models import Reward

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo admin user, sample rewards, and optional test customer"

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@fitlab.com")
        parser.add_argument("--admin-password", default="admin123")
        parser.add_argument("--with-customer", action="store_true")

    def handle(self, *args, **options):
        admin_email = options["admin_email"].lower()
        admin_password = options["admin_password"]

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
