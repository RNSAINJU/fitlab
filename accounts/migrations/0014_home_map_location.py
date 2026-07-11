from urllib.parse import unquote, urlparse, parse_qs

from django.db import migrations, models


def seed_map_location(apps, schema_editor):
    HomePageSettings = apps.get_model("accounts", "HomePageSettings")
    hp = HomePageSettings.objects.filter(pk=1).first()
    if not hp:
        return
    if hp.map_location:
        return
    if hp.contact_address:
        hp.map_location = hp.contact_address.split("\n")[0].strip()
    elif hp.map_embed_url:
        parsed = urlparse(hp.map_embed_url)
        query = parse_qs(parsed.query).get("q", [""])[0]
        hp.map_location = unquote(query) or "The Fit Lab Gym, Bhaktapur, Nepal"
    else:
        hp.map_location = "The Fit Lab Gym, Bhaktapur, Nepal"
    hp.save(update_fields=["map_location"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_home_pricing_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagesettings",
            name="map_location",
            field=models.CharField(
                blank=True,
                default="The Fit Lab Gym, Bhaktapur, Nepal",
                help_text="Address or place name used for the Find Us map.",
                max_length=255,
            ),
        ),
        migrations.RunPython(seed_map_location, migrations.RunPython.noop),
    ]
