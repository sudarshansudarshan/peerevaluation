# Generated by Django 3.2.6 on 2025-01-09 11:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0044_auto_20250109_1646'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incentivization',
            old_name='reward_points',
            new_name='rewards',
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 16, 16, 46, 52, 403592)),
        ),
    ]
