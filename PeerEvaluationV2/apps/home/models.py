from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

# Course Model
class Course(models.Model):
    course_id = models.CharField(max_length=100, help_text="Unique identifier for the course")
    name = models.CharField(max_length=255, help_text="Name of the course, e.g., Machine Learning for Beginners")
    description = models.TextField(null=True, blank=True, help_text="Description of the course")
    is_public = models.BooleanField(default=False, help_text="Indicates whether students can enroll directly")
    start_date = models.DateTimeField(help_text="Start date of the course")
    end_date = models.DateTimeField(help_text="End date of the course")

    def __str__(self):
        return self.name
    
# Batch Model
class Batch(models.Model):
    batch_id = models.CharField(max_length=100, help_text="Unique identifier for the batch")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="batches")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="batches_as_teacher")

    class Meta:
        unique_together = ('course', 'batch_id', 'teacher')  # Ensures uniqueness of the teacher for a batch in a course

    def __str__(self):
        return f"{self.batch_id} - {self.course.name} ({self.teacher.username})"


# Exam Model
class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="exams")
    date = models.DateTimeField(help_text="Date of the Exam")
    number_of_questions = models.IntegerField()
    duration = models.IntegerField(help_text="Duration of the exam in minutes")
    max_scores = models.IntegerField()
    k = models.IntegerField(help_text="Number of evaluations for student")
    completed = models.BooleanField(default=False, help_text="Indicates whether the exam is completed")

    def __str__(self):
        return f"{self.batch.batch_id}"
    
class UIDMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uid_mappings")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="uid_mappings")
    uid = models.CharField(max_length=100, help_text="Unique identifier for the user")

    class Meta:
        unique_together = ('user', 'uid')  # Ensures uniqueness of the uid for a user

    def __str__(self):
        return f"{self.user.username} - {self.uid}"
    

class Documents(models.Model):
    uid = models.CharField(max_length=100, help_text="Unique identifier for the user")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="documents")
    document = models.FileField(upload_to='documents/')
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")


# Peer Evaluation
class PeerEvaluation(models.Model):
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations_made")
    evaluated_on = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=datetime.now() + timedelta(days=7))
    uid = models.IntegerField(help_text="Unique identifier for the user")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peer_evaluations")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="peer_evaluations")
    document = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name="peer_evaluations")
    feedback = models.TextField(help_text="Feedback for the evaluation")
    score = models.TextField(help_text="Score for the evaluation")


# Statistics Model
class Statistics(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="statistics")
    avg_score = models.FloatField()
    std_dev = models.FloatField(help_text="Standard deviation of scores")

    def __str__(self):
        return f"Statistics for {self.batch.batch_id}"
    

# Incentivization Model
class Incentivization(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="incentives")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incentives")
    reward_points = models.IntegerField()

    class Meta:
        unique_together = ('batch', 'student')  # Ensures no duplicate entries for a student in a batch

    def __str__(self):
        return f"{self.student.username} - {self.reward_points} points in {self.batch.batch_id}"
    

    
class StudentEnrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="enrolled_students")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolled_students")
    approval_status = models.BooleanField(default=False, help_text="Indicates whether the enrollment is approved")

    class Meta:
        unique_together = ('student', 'batch')  # Ensures no duplicate entries for a student in a batch

    def __str__(self):
        return f"{self.student.username}"
    

class TeachingAssistantAssociation(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="ta_associations")
    teaching_assistant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ta_associations")

    class Meta:
        unique_together = ('batch', 'teaching_assistant')

    def __str__(self):
        return f"{self.teaching_assistant.username} - {self.batch.batch_id}"
    
    @staticmethod
    def is_ta(user, batch):
        return TeachingAssistantAssociation.objects.filter(teaching_assistant=user, batch=batch).exists()

