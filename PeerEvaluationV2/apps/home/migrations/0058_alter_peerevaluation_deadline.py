# Generated by Django 5.1.6 on 2025-02-11 04:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0057_alter_peerevaluation_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 18, 9, 49, 40, 716029)),
        ),
    ]
