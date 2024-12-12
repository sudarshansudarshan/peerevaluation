from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    login = models.BooleanField(default=False, help_text="Check if the user is currently logged in")
    user_type = models.CharField(
        max_length=50,
        choices=[('Admin', 'Admin'), ('Student', 'Student'), ('Teacher', 'Teacher'), ('TA', 'TA')],
        help_text="Role of the user"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Add related_name attributes to resolve conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups."
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text="Specific permissions for this user."
    )

# Course Model
class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    batch = models.TextField(null=True)
    is_public = models.BooleanField(default=False, null=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)

    def __str__(self):
        return self.name

# Role in Course (Normalized)
class CourseRole(models.Model):
    ROLE_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
        ('TA', 'Teaching Assistant'),
        ('SuperPeer', 'Super Peer')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_roles")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# ExamType Model
class ExamType(models.Model):
    name = models.CharField(max_length=255, help_text="Type of an exam, e.g., Mid term, end term")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exam_types")

    def __str__(self):
        return f"{self.name} ({self.course.name})"

# Exam Model
class Exam(models.Model):
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="exams")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exams_as_teacher")
    date = models.DateTimeField(help_text="Date of the Exam")
    number_of_questions = models.IntegerField()
    max_scores = models.IntegerField()

# Document Model
class Document(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="documents")
    link = models.URLField(help_text="URL of document")
    avg_score = models.FloatField(null=True, blank=True)

# Peer Evaluation
class PeerEvaluation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="peer_evaluations")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="peer_evaluations")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations_made")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="peer_evaluations")
    feedback = models.TextField(help_text="Feedback for the evaluation")
    score = models.IntegerField()

# Statistics Model
class Statistics(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="statistics")
    avg_score = models.FloatField()
    std_dev = models.FloatField(help_text="Standard deviation of scores")

# Incentivization Model
class Incentivization(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="incentives")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incentives")
    reward_points = models.IntegerField()

    class Meta:
        unique_together = ('course', 'student')  # Ensures no duplicate entries