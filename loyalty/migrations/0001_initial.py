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
            name="PointTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.IntegerField()),
                ("transaction_type", models.CharField(choices=[("earn", "Earn"), ("redeem", "Redeem"), ("adjust", "Adjust"), ("referral", "Referral bonus")], max_length=20)),
                ("description", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_point_transactions", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="point_transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
