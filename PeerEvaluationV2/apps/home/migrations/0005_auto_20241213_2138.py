# Generated by Django 3.2.6 on 2024-12-13 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_staffs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='exam_type',
        ),
        migrations.DeleteModel(
            name='ExamType',
        ),
    ]
