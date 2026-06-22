from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="activityevent",
            name="points_amount",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
