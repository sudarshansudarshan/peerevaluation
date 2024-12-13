from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField(null=True, blank=True, default=datetime.now)

    def __str__(self):
        return self.name


class numberOfQuestions(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    total_marks = models.IntegerField(default=0)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} for {self.course_id.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('TA', 'Teaching Assistant'),
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def serialize(self):
        return {
            'id': self.id,
            'username': self.user.username,
            'role': self.role
        }


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    uid = models.IntegerField(unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'course_id'], name='unique_student_course')
        ]

    def __str__(self):
        return f"{self.student_id.username} - {self.course_id.name}"


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    peer_evaluations = models.ManyToManyField(
        'PeerEvaluation',
        related_name='evaluated_documents'  # Updated related_name
    )
    uid = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='student_documents')
    file = models.FileField(upload_to='documents/')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_documents')

    def __str__(self):
        return self.title


class PeerEvaluation(models.Model):
    evaluator_id = models.IntegerField()
    evaluation_date = models.DateTimeField(auto_now_add=True)
    evaluation = models.TextField()
    feedback = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='peer_evaluations')
    score = models.IntegerField()
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='document_peer_evaluations'  # Updated related_name
    )
    evaluated = models.BooleanField(default=False)
    ticket = models.IntegerField(default=0)
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='evaluated_by')

    def __str__(self):
        return f'Peer Evaluation for Document {self.document.title}'