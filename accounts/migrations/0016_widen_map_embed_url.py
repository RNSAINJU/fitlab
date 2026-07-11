from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0015_fix_map_location_share_links"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepagesettings",
            name="map_embed_url",
            field=models.URLField(
                blank=True,
                default="https://maps.google.com/maps?q=Kathmandu%2C%20Nepal&z=13&output=embed",
                max_length=2000,
            ),
        ),
    ]
