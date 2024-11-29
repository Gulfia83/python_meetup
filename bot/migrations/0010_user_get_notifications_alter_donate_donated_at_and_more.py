# Generated by Django 4.1.5 on 2024-11-28 06:50

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0009_application_accepted_alter_application_applicant_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="get_notifications",
            field=models.BooleanField(default=False, verbose_name="Получать рассылку"),
        ),
        migrations.AlterField(
            model_name="donate",
            name="donated_at",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 11, 28, 6, 50, 58, 975654, tzinfo=datetime.timezone.utc),
                verbose_name="Время доната",
            ),
        ),
        migrations.AlterField(
            model_name="questions",
            name="asked_at",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 11, 28, 6, 50, 58, 976653, tzinfo=datetime.timezone.utc),
                verbose_name="Время создания",
            ),
        ),
    ]
