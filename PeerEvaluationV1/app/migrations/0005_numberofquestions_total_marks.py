# Generated by Django 3.0.7 on 2024-12-11 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_peerevaluation_evaluated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='numberofquestions',
            name='total_marks',
            field=models.IntegerField(default=0),
        ),
    ]