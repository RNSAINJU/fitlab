from django import forms

from .models import Reward


class RewardForm(forms.ModelForm):
    stock = forms.IntegerField(
        required=False,
        min_value=0,
        label="Stock (optional)",
        help_text="Leave blank for unlimited availability.",
        widget=forms.NumberInput(attrs={"placeholder": "Unlimited"}),
    )

    class Meta:
        model = Reward
        fields = ("title", "description", "points_cost", "image_emoji", "stock", "is_active")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Free protein shake"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Describe the reward for customers"}),
            "points_cost": forms.NumberInput(attrs={"min": 1, "placeholder": "250"}),
            "image_emoji": forms.TextInput(attrs={"placeholder": "🎁", "maxlength": 8}),
        }
        labels = {
            "points_cost": "Required TFL Points",
            "image_emoji": "Icon emoji",
            "is_active": "Visible in customer marketplace",
        }

    def clean_points_cost(self):
        points = self.cleaned_data["points_cost"]
        if points < 1:
            raise forms.ValidationError("Points must be at least 1.")
        return points

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock in (None, ""):
            return None
        return stock

    def save(self, commit=True):
        reward = super().save(commit=False)
        if self.cleaned_data.get("stock") is None:
            reward.stock = None
        if commit:
            reward.save()
        return reward
