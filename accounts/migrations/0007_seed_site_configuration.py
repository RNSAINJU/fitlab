from django.db import migrations


def seed_site_configuration(apps, schema_editor):
    SiteConfiguration = apps.get_model("accounts", "SiteConfiguration")
    Site = apps.get_model("sites", "Site")
    site_name = "The Fitlab"
    site = Site.objects.filter(pk=1).first()
    if site and site.name:
        site_name = site.name
    SiteConfiguration.objects.get_or_create(pk=1, defaults={"site_name": site_name})


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_siteconfiguration"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(seed_site_configuration, migrations.RunPython.noop),
    ]
