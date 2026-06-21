import os

from django.db import migrations


def configure_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    domain = os.environ.get("FITLAB_SITE_DOMAIN", "localhost:8000")
    Site.objects.update_or_create(
        pk=1,
        defaults={"domain": domain, "name": "Fitlab"},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(configure_site, migrations.RunPython.noop),
    ]
