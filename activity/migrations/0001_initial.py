import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=40)),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activity_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
