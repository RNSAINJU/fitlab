from django.db import migrations


def update_site_name(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(pk=1).update(name="The Fitlab")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_configure_site"),
    ]

    operations = [
        migrations.RunPython(update_site_name, migrations.RunPython.noop),
    ]
