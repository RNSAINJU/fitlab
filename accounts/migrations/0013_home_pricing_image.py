from django.db import migrations, models

import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_default_light_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagesettings",
            name="pricing_image",
            field=models.ImageField(blank=True, upload_to=accounts.models.home_pricing_banner_path),
        ),
        migrations.AddField(
            model_name="homepagesettings",
            name="pricing_image_alt",
            field=models.CharField(blank=True, default="Gym pricing", max_length=160),
        ),
        migrations.AddField(
            model_name="homepagesettings",
            name="pricing_image_url",
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name="homepagesettings",
            name="rates_title",
            field=models.CharField(default="Pricing", max_length=120),
        ),
    ]
