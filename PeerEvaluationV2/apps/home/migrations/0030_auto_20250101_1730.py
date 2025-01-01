# Generated by Django 3.2.6 on 2025-01-01 12:00

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0029_auto_20250101_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseTopic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('topic', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.batch')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.course')),
            ],
        ),
        migrations.AlterField(
            model_name='peerevaluation',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 8, 17, 30, 54, 150994)),
        ),
        migrations.CreateModel(
            name='LLMEvaluation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('answer', models.TextField()),
                ('feedback', models.TextField()),
                ('score', models.TextField()),
                ('ai', models.TextField()),
                ('aggregate', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('Topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.coursetopic')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
