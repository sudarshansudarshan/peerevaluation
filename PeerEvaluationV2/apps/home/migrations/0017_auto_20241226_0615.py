# Generated by Django 3.2.6 on 2024-12-26 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_remove_batch_teaching_assistant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentenrollment',
            name='uid',
        ),
        migrations.AddField(
            model_name='exam',
            name='duration',
            field=models.IntegerField(default=0, help_text='Duration of the exam in minutes'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='peer_evaluations', to='home.document'),
        ),
    ]
