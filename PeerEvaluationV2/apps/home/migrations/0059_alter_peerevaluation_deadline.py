# Generated by Django 5.1.6 on 2025-02-12 08:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0058_alter_peerevaluation_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 19, 13, 46, 12, 216206)),
        ),
    ]
