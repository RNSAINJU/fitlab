import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loyalty", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PointRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("points_amount", models.PositiveIntegerField()),
                ("icon_emoji", models.CharField(default="⚡", max_length=8)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.AddField(
            model_name="pointtransaction",
            name="rule",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="loyalty.pointrule",
            ),
        ),
        migrations.AlterField(
            model_name="pointtransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("earn", "Earn"),
                    ("redeem", "Redeem"),
                    ("adjust", "Adjust"),
                    ("referral", "Referral bonus"),
                    ("rule", "Point rule"),
                ],
                max_length=20,
            ),
        ),
    ]
