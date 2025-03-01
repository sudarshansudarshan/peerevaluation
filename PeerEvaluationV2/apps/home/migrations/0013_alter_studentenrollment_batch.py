# Generated by Django 3.2.6 on 2024-12-16 05:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_alter_studentenrollment_batch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentenrollment',
            name='batch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_students', to='home.batch'),
            preserve_default=False,
        ),
    ]
