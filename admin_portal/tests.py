from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from loyalty.models import PointTransaction

User = get_user_model()


class AdminPortalPostValidationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )
        self.customer = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="StrongPass123!",
            approval_status=User.ApprovalStatus.APPROVED,
        )
        self.client.force_login(self.staff)

    def test_invalid_adjustment_amount_does_not_crash_or_create_transaction(self):
        response = self.client.post(
            reverse("admin_portal:points_ledger"),
            {
                "action": "adjust",
                "user_id": str(self.customer.pk),
                "amount": "",
            },
        )

        self.assertRedirects(response, reverse("admin_portal:points_ledger"))
        self.assertFalse(PointTransaction.objects.exists())

    def test_invalid_redemption_id_does_not_crash(self):
        response = self.client.post(
            reverse("admin_portal:points_ledger"),
            {
                "action": "approve_redemption",
                "redemption_id": "not-a-number",
            },
        )

        self.assertRedirects(response, reverse("admin_portal:points_ledger"))

    def test_invalid_approval_user_id_does_not_crash(self):
        response = self.client.post(
            reverse("admin_portal:registration_approvals"),
            {
                "action": "approve",
                "user_id": "not-a-number",
            },
        )

        self.assertRedirects(response, reverse("admin_portal:registration_approvals"))
