from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_site_name_the_fitlab"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="member_id",
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
    ]
