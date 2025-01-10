# Generated by Django 3.2.6 on 2025-01-09 11:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0043_auto_20250109_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='incentivization',
            name='exam_count',
            field=models.IntegerField(default=0, help_text='Number of exams attempted by the student'),
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 16, 16, 46, 14, 157398)),
        ),
    ]