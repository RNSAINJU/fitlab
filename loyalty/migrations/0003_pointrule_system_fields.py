import django.db.models.deletion
from django.db import migrations, models


def seed_default_rules(apps, schema_editor):
    PointRule = apps.get_model("loyalty", "PointRule")
    defaults = [
        {
            "slug": "registration",
            "title": "New Registration",
            "description": "Awarded when a new member registration is approved.",
            "rule_kind": "fixed",
            "trigger": "on_approval",
            "points_amount": 10,
            "icon_emoji": "🎉",
            "is_system": True,
            "is_active": True,
        },
        {
            "slug": "daily_login",
            "title": "Daily Login",
            "description": "Awarded once per day when a member logs in.",
            "rule_kind": "fixed",
            "trigger": "on_daily_login",
            "points_amount": 1,
            "icon_emoji": "📅",
            "is_system": True,
            "is_active": True,
        },
        {
            "slug": "referral",
            "title": "Refer a Friend",
            "description": "Awarded when a referred member is approved.",
            "rule_kind": "fixed",
            "trigger": "on_referral",
            "points_amount": 5,
            "icon_emoji": "🤝",
            "is_system": True,
            "is_active": True,
        },
        {
            "slug": "gym_activity",
            "title": "Gym Activity",
            "description": "Manually award points for classes, check-ins, challenges, and other gym activities.",
            "rule_kind": "fixed",
            "trigger": "manual",
            "points_amount": 25,
            "icon_emoji": "🏋️",
            "is_system": True,
            "is_active": True,
        },
        {
            "slug": "payment",
            "title": "Payment Reward",
            "description": "Award points based on member spend. Default: 10 TFL Points per 1000 spent.",
            "rule_kind": "payment_spend",
            "trigger": "manual",
            "points_amount": 10,
            "spend_amount": 1000,
            "icon_emoji": "💳",
            "is_system": True,
            "is_active": True,
        },
    ]
    for rule_data in defaults:
        slug = rule_data.pop("slug")
        PointRule.objects.update_or_create(slug=slug, defaults=rule_data)


class Migration(migrations.Migration):

    dependencies = [
        ("loyalty", "0002_pointrule_pointtransaction_rule"),
    ]

    operations = [
        migrations.AddField(
            model_name="pointrule",
            name="is_system",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="pointrule",
            name="rule_kind",
            field=models.CharField(
                choices=[("fixed", "Fixed points"), ("payment_spend", "Payment spend")],
                default="fixed",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="pointrule",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="pointrule",
            name="spend_amount",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Currency spent per points block (e.g. 1000 for payment rules).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="pointrule",
            name="trigger",
            field=models.CharField(
                choices=[
                    ("manual", "Manual (admin)"),
                    ("on_approval", "On registration approval"),
                    ("on_daily_login", "On daily login"),
                    ("on_referral", "On referral approval"),
                ],
                default="manual",
                max_length=20,
            ),
        ),
        migrations.RunPython(seed_default_rules, migrations.RunPython.noop),
    ]
