from django import forms

from .models import PointRule, PointRuleKind, PointRuleTrigger


class PointRuleForm(forms.ModelForm):
    class Meta:
        model = PointRule
        fields = ("title", "description", "points_amount", "icon_emoji", "is_active")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Weekend challenge"}),
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Describe when this rule should be used"}),
            "points_amount": forms.NumberInput(attrs={"min": 1, "placeholder": "50"}),
            "icon_emoji": forms.TextInput(attrs={"placeholder": "🏆", "maxlength": 8}),
        }
        labels = {
            "points_amount": "TFL Points to award",
            "icon_emoji": "Icon emoji",
            "is_active": "Available for distribution",
        }

    def clean_points_amount(self):
        points = self.cleaned_data["points_amount"]
        if points < 1:
            raise forms.ValidationError("Points must be at least 1.")
        return points


class SystemRuleForm(forms.ModelForm):
    class Meta:
        model = PointRule
        fields = ("points_amount", "spend_amount", "description", "is_active")
        widgets = {
            "points_amount": forms.NumberInput(attrs={"min": 1}),
            "spend_amount": forms.NumberInput(attrs={"min": 1}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "points_amount": "TFL Points",
            "spend_amount": "Spend amount",
            "is_active": "Rule enabled",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.rule_kind != PointRuleKind.PAYMENT_SPEND:
            self.fields.pop("spend_amount", None)

    def clean(self):
        cleaned = super().clean()
        if self.instance.rule_kind == PointRuleKind.PAYMENT_SPEND:
            if not cleaned.get("spend_amount"):
                raise forms.ValidationError("Payment rules require a spend amount.")
            if not cleaned.get("points_amount"):
                raise forms.ValidationError("Payment rules require a points amount.")
        return cleaned
