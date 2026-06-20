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
            name="ReferralRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bonus_awarded", models.BooleanField(default=False)),
                ("bonus_points", models.PositiveIntegerField(default=0)),
                ("awarded_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("referee", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="referral_record", to=settings.AUTH_USER_MODEL)),
                ("referrer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="referral_records", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
