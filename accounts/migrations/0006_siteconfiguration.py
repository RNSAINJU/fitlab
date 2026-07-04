from django.db import migrations, models

import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_user_address_member_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="The Fitlab", max_length=120)),
                ("logo", models.ImageField(blank=True, upload_to=accounts.models.site_logo_path)),
            ],
            options={
                "verbose_name": "Site configuration",
                "verbose_name_plural": "Site configuration",
            },
        ),
    ]
