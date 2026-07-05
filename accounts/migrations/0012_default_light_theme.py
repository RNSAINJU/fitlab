from django.db import migrations, models


def set_default_light_theme(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(theme_preference="dark").update(theme_preference="light")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_user_theme_preference"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="theme_preference",
            field=models.CharField(
                choices=[("dark", "Dark"), ("light", "Light")],
                default="light",
                max_length=10,
            ),
        ),
        migrations.RunPython(set_default_light_theme, migrations.RunPython.noop),
    ]
