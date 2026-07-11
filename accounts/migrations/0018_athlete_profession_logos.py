from django.db import migrations, models

import accounts.models


def rename_powerlifters_section(apps, schema_editor):
    HomePageSettings = apps.get_model("accounts", "HomePageSettings")
    settings = HomePageSettings.objects.filter(pk=1).first()
    if settings and settings.powerlifters_title == "Powerlifters":
        settings.powerlifters_title = "Athlete"
        settings.save(update_fields=["powerlifters_title"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_theme_logos"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagesettings",
            name="athlete_logo_kickboxing",
            field=models.ImageField(blank=True, upload_to=accounts.models.home_athlete_logo_path),
        ),
        migrations.AddField(
            model_name="homepagesettings",
            name="athlete_logo_kickboxing_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="homepagesettings",
            name="athlete_logo_powerlifting",
            field=models.ImageField(blank=True, upload_to=accounts.models.home_athlete_logo_path),
        ),
        migrations.AddField(
            model_name="homepagesettings",
            name="athlete_logo_powerlifting_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="homepowerlifter",
            name="profession",
            field=models.CharField(
                choices=[("powerlifting", "Powerlifting"), ("kickboxing", "Kick Boxing")],
                default="powerlifting",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="homepagesettings",
            name="powerlifters_title",
            field=models.CharField(default="Athlete", max_length=120),
        ),
        migrations.RunPython(rename_powerlifters_section, migrations.RunPython.noop),
    ]
