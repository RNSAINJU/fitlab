import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Reward",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("points_cost", models.PositiveIntegerField()),
                ("image_emoji", models.CharField(default="🎁", max_length=8)),
                ("is_active", models.BooleanField(default=True)),
                ("stock", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["points_cost"],
            },
        ),
        migrations.CreateModel(
            name="RedemptionRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("points_cost", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=20)),
                ("admin_note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_redemptions", to=settings.AUTH_USER_MODEL)),
                ("reward", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="redemptions", to="rewards.reward")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="redemptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
