from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from loyalty.services import get_balance
from referrals.models import ReferralRecord

from .forms import RegistrationForm

User = get_user_model()


class RegistrationTests(TestCase):
    def test_register_uses_referral_code_saved_from_query_string(self):
        referrer = User.objects.create_user(
            username="coach@example.com",
            email="coach@example.com",
            password="StrongPass123!",
            approval_status=User.ApprovalStatus.APPROVED,
        )

        response = self.client.get(
            f"{reverse('accounts:register')}?ref={referrer.referral_code.lower()}"
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "New Athlete",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "terms_accepted": "on",
            },
        )

        self.assertRedirects(response, reverse("accounts:pending"))
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.referred_by, referrer)

    def test_registration_rejects_unknown_referral_code(self):
        form = RegistrationForm(
            data={
                "full_name": "New Athlete",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "referral_code": "UNKNOWN",
                "terms_accepted": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("referral_code", form.errors)


class LoginTests(TestCase):
    def test_login_accepts_mixed_case_email(self):
        User.objects.create_user(
            username="athlete@example.com",
            email="athlete@example.com",
            password="StrongPass123!",
            approval_status=User.ApprovalStatus.APPROVED,
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "Athlete@Example.com", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))


class ApprovalBonusTests(TestCase):
    def test_approval_awards_signup_and_referral_bonuses_once(self):
        referrer = User.objects.create_user(
            username="referrer@example.com",
            email="referrer@example.com",
            password="StrongPass123!",
            approval_status=User.ApprovalStatus.APPROVED,
        )
        referee = User.objects.create_user(
            username="referee@example.com",
            email="referee@example.com",
            password="StrongPass123!",
            referred_by=referrer,
        )

        referee.approval_status = User.ApprovalStatus.APPROVED
        referee.save(update_fields=["approval_status"])

        self.assertEqual(get_balance(referee), settings.SIGNUP_BONUS_POINTS)
        self.assertEqual(get_balance(referrer), settings.REFERRAL_BONUS_POINTS)
        record = ReferralRecord.objects.get(referrer=referrer, referee=referee)
        self.assertTrue(record.bonus_awarded)
        self.assertEqual(record.bonus_points, settings.REFERRAL_BONUS_POINTS)

        referee.approval_status = User.ApprovalStatus.REJECTED
        referee.save(update_fields=["approval_status"])
        referee.approval_status = User.ApprovalStatus.APPROVED
        referee.save(update_fields=["approval_status"])

        self.assertEqual(get_balance(referee), settings.SIGNUP_BONUS_POINTS)
        self.assertEqual(get_balance(referrer), settings.REFERRAL_BONUS_POINTS)
