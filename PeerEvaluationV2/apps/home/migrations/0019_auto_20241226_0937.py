# Generated by Django 3.2.6 on 2024-12-26 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0018_alter_exam_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='completed',
            field=models.BooleanField(default=False, help_text='Indicates whether the exam is completed'),
        ),
        migrations.CreateModel(
            name='UIDMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(help_text='Unique identifier for the user', max_length=100)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uid_mappings', to='home.exam')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uid_mappings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'uid')},
            },
        ),
    ]
