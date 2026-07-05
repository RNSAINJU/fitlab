from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_home_hero_subtext"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="theme_preference",
            field=models.CharField(
                choices=[("dark", "Dark"), ("light", "Light")],
                default="dark",
                max_length=10,
            ),
        ),
    ]
