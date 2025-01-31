# Generated by Django 3.2.6 on 2024-12-13 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the course, e.g., Machine Learning for Beginners', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of the course', null=True)),
                ('batch', models.TextField(blank=True, null=True)),
                ('is_public', models.BooleanField(default=False, help_text='Indicates whether students can enroll directly')),
                ('start_date', models.DateTimeField(help_text='Start date of the course')),
                ('end_date', models.DateTimeField(help_text='End date of the course')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(help_text='URL of document')),
                ('avg_score', models.FloatField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='home.course')),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(help_text='Date of the Exam')),
                ('number_of_questions', models.IntegerField()),
                ('max_scores', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='home.course')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avg_score', models.FloatField()),
                ('std_dev', models.FloatField(help_text='Standard deviation of scores')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='home.course')),
            ],
        ),
        migrations.CreateModel(
            name='PeerEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField(help_text='Feedback for the evaluation')),
                ('score', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_evaluations', to='home.course')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_evaluations', to='home.document')),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations_made', to=settings.AUTH_USER_MODEL)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_evaluations', to='home.exam')),
            ],
        ),
        migrations.CreateModel(
            name='ExamType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Type of an exam, e.g., Mid term, end term', max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_types', to='home.course')),
            ],
        ),
        migrations.AddField(
            model_name='exam',
            name='exam_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='home.examtype'),
        ),
        migrations.AddField(
            model_name='exam',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams_as_teacher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CourseRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('Teacher', 'Teacher'), ('Student', 'Student'), ('TA', 'Teaching Assistant'), ('SuperPeer', 'Super Peer')], max_length=20)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='home.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Incentivization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward_points', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incentives', to='home.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incentives', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('course', 'student')},
            },
        ),
    ]
