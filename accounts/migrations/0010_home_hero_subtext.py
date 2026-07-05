from django.db import migrations, models


def seed_hero_copy(apps, schema_editor):
    HomePageSettings = apps.get_model("accounts", "HomePageSettings")
    hp = HomePageSettings.objects.filter(pk=1).first()
    if not hp:
        return
    if hp.hero_headline in ("Ready to start?", ""):
        hp.hero_headline = "Recruit Yourself"
    if not hp.hero_subtext:
        hp.hero_subtext = "Join the elite lab where data meets dedication."
    hp.save(update_fields=["hero_headline", "hero_subtext"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_seed_home_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagesettings",
            name="hero_subtext",
            field=models.CharField(
                blank=True,
                default="Join the elite lab where data meets dedication.",
                max_length=240,
            ),
        ),
        migrations.AlterField(
            model_name="homepagesettings",
            name="hero_headline",
            field=models.CharField(default="Recruit Yourself", max_length=200),
        ),
        migrations.RunPython(seed_hero_copy, migrations.RunPython.noop),
    ]
