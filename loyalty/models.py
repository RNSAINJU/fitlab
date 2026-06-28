from django.conf import settings
from django.db import models


from django.conf import settings
from django.db import models


class PointRuleKind(models.TextChoices):
    FIXED = "fixed", "Fixed points"
    PAYMENT_SPEND = "payment_spend", "Payment spend"


class PointRuleTrigger(models.TextChoices):
    MANUAL = "manual", "Manual (admin)"
    ON_APPROVAL = "on_approval", "On registration approval"
    ON_DAILY_LOGIN = "on_daily_login", "On daily login"
    ON_REFERRAL = "on_referral", "On referral approval"


class PointRule(models.Model):
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    rule_kind = models.CharField(
        max_length=20,
        choices=PointRuleKind.choices,
        default=PointRuleKind.FIXED,
    )
    trigger = models.CharField(
        max_length=20,
        choices=PointRuleTrigger.choices,
        default=PointRuleTrigger.MANUAL,
    )
    points_amount = models.PositiveIntegerField()
    spend_amount = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Currency spent per points block (e.g. 1000 for payment rules).",
    )
    icon_emoji = models.CharField(max_length=8, default="⚡")
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        if self.rule_kind == PointRuleKind.PAYMENT_SPEND and self.spend_amount:
            return f"{self.title} ({self.points_amount} TFL per {self.spend_amount} spent)"
        return f"{self.title} ({self.points_amount} TFL)"

    @property
    def is_manual(self):
        return self.trigger == PointRuleTrigger.MANUAL

    def calculate_points(self, amount_spent=None, custom_points=None):
        if custom_points is not None:
            return custom_points
        if self.rule_kind == PointRuleKind.PAYMENT_SPEND:
            if not amount_spent or not self.spend_amount:
                return 0
            return (amount_spent * self.points_amount) // self.spend_amount
        return self.points_amount


class PointTransaction(models.Model):
    class TransactionType(models.TextChoices):
        EARN = "earn", "Earn"
        REDEEM = "redeem", "Redeem"
        ADJUST = "adjust", "Adjust"
        REFERRAL = "referral", "Referral bonus"
        RULE = "rule", "Point rule"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="point_transactions")
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    description = models.CharField(max_length=255)
    rule = models.ForeignKey(
        PointRule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_point_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.user} {sign}{self.amount} ({self.transaction_type})"
