# Generated by Django 3.2.6 on 2025-01-08 09:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0039_auto_20250108_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='peerevaluation',
            name='evaluations_sent',
            field=models.BooleanField(default=False, help_text='Indicates whether the evaluations are sent'),
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 15, 15, 28, 31, 737065)),
        ),
    ]