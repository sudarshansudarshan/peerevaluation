# Generated by Django 3.2.6 on 2025-01-01 09:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20250101_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 8, 14, 57, 38, 291098)),
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='uid',
            field=models.CharField(help_text='Unique identifier for the user', max_length=100),
        ),
    ]
