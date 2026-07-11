from django.db import migrations, models


def rename_kickboxing_to_boxing(apps, schema_editor):
    HomePowerlifter = apps.get_model("accounts", "HomePowerlifter")
    HomePowerlifter.objects.filter(profession="kickboxing").update(profession="boxing")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0018_athlete_profession_logos"),
    ]

    operations = [
        migrations.RenameField(
            model_name="homepagesettings",
            old_name="athlete_logo_kickboxing",
            new_name="athlete_logo_boxing",
        ),
        migrations.RenameField(
            model_name="homepagesettings",
            old_name="athlete_logo_kickboxing_url",
            new_name="athlete_logo_boxing_url",
        ),
        migrations.AlterField(
            model_name="homepowerlifter",
            name="profession",
            field=models.CharField(
                choices=[("powerlifting", "Powerlifting"), ("boxing", "Boxing")],
                default="powerlifting",
                max_length=20,
            ),
        ),
        migrations.RunPython(rename_kickboxing_to_boxing, migrations.RunPython.noop),
    ]
