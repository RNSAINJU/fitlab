from django.db import migrations


def clear_share_links_from_map_location(apps, schema_editor):
    HomePageSettings = apps.get_model("accounts", "HomePageSettings")
    hp = HomePageSettings.objects.filter(pk=1).first()
    if not hp:
        return
    location = (hp.map_location or "").strip()
    if location.startswith("http") and "/maps/embed" not in location and "output=embed" not in location:
        hp.map_location = "The Fit Lab Gym, Bhaktapur, Nepal"
        hp.save(update_fields=["map_location"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0014_home_map_location"),
    ]

    operations = [
        migrations.RunPython(clear_share_links_from_map_location, migrations.RunPython.noop),
    ]
