# Generated by Django 5.1.4 on 2024-12-18 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_numberofquestions_k'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='password_updated',
            field=models.BooleanField(default=False),
        ),
    ]
