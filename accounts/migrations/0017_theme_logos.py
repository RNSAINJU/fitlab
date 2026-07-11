from django.db import migrations, models

import accounts.models


def copy_legacy_logo(apps, schema_editor):
    SiteConfiguration = apps.get_model("accounts", "SiteConfiguration")
    config = SiteConfiguration.objects.filter(pk=1).first()
    if not config or not config.logo:
        return
    updates = []
    if not config.logo_light:
        config.logo_light = config.logo
        updates.append("logo_light")
    if not config.logo_dark:
        config.logo_dark = config.logo
        updates.append("logo_dark")
    if updates:
        config.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0016_widen_map_embed_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="logo_dark",
            field=models.ImageField(blank=True, upload_to=accounts.models.site_logo_dark_path),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="logo_light",
            field=models.ImageField(blank=True, upload_to=accounts.models.site_logo_light_path),
        ),
        migrations.RunPython(copy_legacy_logo, migrations.RunPython.noop),
    ]
