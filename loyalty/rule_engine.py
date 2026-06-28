from django.utils import timezone

from .models import PointRule, PointRuleKind, PointRuleTrigger, PointTransaction
from .rule_defaults import DEFAULT_POINT_RULES
from .services import award_points


def ensure_default_point_rules():
    for rule_data in DEFAULT_POINT_RULES:
        slug = rule_data["slug"]
        defaults = {key: value for key, value in rule_data.items() if key != "slug"}
        PointRule.objects.update_or_create(slug=slug, defaults=defaults)


def get_point_rule(slug):
    return PointRule.objects.filter(slug=slug, is_active=True).first()


def user_has_rule_award(user, rule):
    return PointTransaction.objects.filter(user=user, rule=rule).exists()


def user_has_daily_login_award(user, rule):
    today = timezone.localdate()
    return PointTransaction.objects.filter(
        user=user,
        rule=rule,
        created_at__date=today,
    ).exists()


def award_rule_points(
    user,
    rule,
    admin_user=None,
    note="",
    amount_spent=None,
    custom_points=None,
):
    points = rule.calculate_points(amount_spent=amount_spent, custom_points=custom_points)
    if points <= 0:
        return None

    description = rule.title
    if rule.rule_kind == PointRuleKind.PAYMENT_SPEND and amount_spent:
        description = f"{rule.title}: {amount_spent} spent"
    elif note:
        description = f"{rule.title} — {note}"
    elif rule.description:
        description = f"{rule.title}: {rule.description}"

    return award_points(
        user=user,
        amount=points,
        transaction_type=PointTransaction.TransactionType.RULE,
        description=description[:255],
        created_by=admin_user,
        rule=rule,
    )


def try_award_registration_points(user):
    rule = get_point_rule("registration")
    if not rule or user_has_rule_award(user, rule):
        return None
    return award_rule_points(user, rule)


def try_award_daily_login_points(user):
    rule = get_point_rule("daily_login")
    if not rule or user_has_daily_login_award(user, rule):
        return None
    return award_rule_points(user, rule)


def try_award_referral_points(referrer, referee):
    rule = get_point_rule("referral")
    if not rule:
        return None

    already_awarded = PointTransaction.objects.filter(
        user=referrer,
        rule=rule,
        description__icontains=referee.display_name,
    ).exists()
    if already_awarded:
        return None

    return award_rule_points(
        referrer,
        rule,
        note=f"Referred {referee.display_name}",
    )


def on_user_approved(user):
    try_award_registration_points(user)

    if user.referred_by_id:
        from referrals.services import award_referrer_on_approval

        award_referrer_on_approval(user)
