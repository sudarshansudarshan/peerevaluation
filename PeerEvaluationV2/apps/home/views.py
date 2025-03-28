from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomPasswordChangeForm
from django.shortcuts import get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import is_aware
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import ExpressionWrapper, F, DateTimeField
from django.utils import timezone
import pytz
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode
from PIL import Image
import io
import tempfile
from django.db.models import Avg, StdDev, Q
from fpdf import FPDF
import qrcode
import tempfile
from PyPDF2 import PdfMerger
import os
from io import BytesIO
import networkx as nx
import math
import google.generativeai as genai
import time
from django.core.mail import send_mail
import numpy as np
import threading
import zipfile
import random
import string
import ast
import array
import csv
import json


genai.configure(api_key="AIzaSyAb4TTvJNOcSeZe4BgwvUrBgUQeAoYvNXI")


def geminiGenerate(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text


def parse_llama_json(text):
    # Extract JSON part from the generated text
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1

    if start_idx == -1 or end_idx == -1:
        raise ValueError("No valid JSON found in the text")

    json_part = text[start_idx:end_idx]

    # Parse the extracted JSON
    try:
        parsed_data = json.loads(json_part)
        return parsed_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def evaluate_answers(answer1, answer2, topic, description):
    prompt = f"""
    The topic of discussion was: """ + topic + ":" + description + """. I want to evaluate the following student answers:
    
    **Task:** As an AI Assistant, assess the answers provided based on their originality, quality, and relevance to the topic. Also, evaluate the percentage of AI-generated content in the answers. Provide the output in **JSON format** with the following structure:
    
    **Evaluation Criteria:**
    1. **Score (0 to 10):** Reflects the quality, depth, and relevance of the answer.
    2. **AI Plagiarism Score (0 to 1):** Indicates the likelihood of the content being AI-generated or plagiarized from online sources.

    **Expected JSON Response Format:**
    ```json
    {
        "question 1": {
            "score": <quality_score_between_0_to_10>,
            "ai": <ai_plagiarism_score_between_0_to_10>,
            "feedback": "<optional_feedback_message>"
        },
        "question 2": {
            "score": <quality_score_between_0_to_10>,
            "ai": <ai_plagiarism_score_between_0_to_10>
            "feedback": "<optional_feedback_message>"
        }
    }
    ```
    
    **Student Answers:**
    - Question 1: """ + answer1 + """
    - Question 2: """ + answer2 + """

    Ensure the response strictly follows the JSON format and provides clear scores for each answer.
    """
    
    scores = parse_llama_json(geminiGenerate(prompt))

    # Calculate aggregate score (penalizing AI plagiarism)
    aggregate_score = (
        (scores['question 1']['score'] * (1 - scores['question 1']['ai'])) +
        (scores['question 2']['score'] * (1 - scores['question 2']['ai']))
    )/2

    # Return the aggregate results
    return {
        "aggregate_score": round(aggregate_score, 2),
        "answers": " ".join([answer1, answer2]),
        "feedback": " ".join([scores['question 1']['feedback'], scores['question 2']['feedback']]),
        "ai_scores": [scores['question 1']['ai'], scores['question 2']['ai']],
        "scores": [scores['question 1']['score'], scores['question 2']['score']]
    }


def flag_evaluations_with_high_std(exam_instance, request, threshold=1.0):
    """
    Flags an exam instance if an evaluation's standard deviation is significantly higher 
    than the average standard deviation of all evaluations.

    Parameters:
    - exam_instance: The exam instance to analyze.
    - threshold: Multiplier for standard deviation; if an evaluation's deviation exceeds 
                 this, it's flagged.
    """

    # Retrieve all evaluations for the given exam score is not empty string
    evaluations = PeerEvaluation.objects.filter(exam=exam_instance, score__isnull=False)
    if not evaluations.exists():
        print(f"No evaluations found for exam {exam_instance}.")
        return

    # Extract scores from evaluations (ensure they are numeric)
    scores = []
    for evaluation in evaluations:
        try:
            score = float(evaluation.total)  # Replace with the actual field storing evaluation scores
            scores.append(score)
        except ValueError:
            print(f"Invalid score for evaluation ID {evaluation.id}: {evaluation.score}")
            continue

    # Ensure scores are numeric before proceeding
    if not scores:
        print(f"No valid scores found for exam {exam_instance}.")
        return

    # Calculate standard deviation for all scores
    scores_array = np.array(scores)
    global_std = scores_array.std()

    # Determine the threshold for flagging
    std_threshold = threshold * global_std

    # Check individual evaluations
    flagged = False
    for evaluation in evaluations:
        evaluator_scores = np.array([
            float(eval.total) for eval in evaluations 
            if eval.evaluator == evaluation.evaluator
        ])
        evaluator_std = evaluator_scores.std()

        if evaluator_std > std_threshold:
            flagged = True
            evaluation.ticket = True
            evaluation.save()
        else:
            incentive = Incentivization.objects.filter(student=evaluation.evaluator, batch=evaluation.exam.batch).first()
            total_exams = UIDMapping.objects.filter(exam__batch=evaluation.exam.batch).count()
            alpha = 0.1
            exam_count = PeerEvaluation.objects.filter(student=evaluation.evaluator, exam__batch=evaluation.exam.batch, score__isnull=False).values('exam_id').distinct().count()
            print(f"Exam count: {exam_count}")
            incremental_reward = (1 / (1 + math.exp(-alpha * exam_count))) / total_exams
            
            if incentive:
                print(incentive)
                incentive.rewards = min(incentive.rewards + incremental_reward, 1.0)
                incentive.exam_count = exam_count
                incentive.save()
            else:
                print(incentive)
                Incentivization.objects.create(
                    student=evaluation.evaluator,
                    batch=evaluation.exam.batch,
                    rewards=min(incremental_reward, 1.0),
                    exam_count=1
                )
    
    # if flagged:
    #     exam_instance.flags = True
    #     exam_instance.save()


def is_superuser(self):
    return self.is_superuser
User.add_to_class('is_superuser', is_superuser)


# Overwrite User table from django to add method is_student
def is_student(self):
    return not self.is_staff and not self.is_superuser
User.add_to_class('is_student', is_student)


# Overwrite User table from django to add method is_staff
def is_staff(self):
    return self.is_staff
User.add_to_class('is_staff', is_staff)


def is_teacher(self):
    return self.is_staff and not self.is_superuser
User.add_to_class('is_teacher', is_teacher)

def is_ta(self):
    return TeachingAssistantAssociation.objects.filter(teaching_assistant=self).exists()
User.add_to_class('is_ta', is_ta)


def generate_random_text():
    return ''.join(random.choices(string.ascii_lowercase, k=10))


def convert_pdf_to_image_and_decode_qr(pdf_bytes):
    """
    Convert the first page of a PDF to a PNG image and look for any QR codes.
    Parameters:
        pdf_bytes: The PDF file as bytes.
    Returns:
        qr_data: The decoded QR code data if found, or None.
    """
    try:
        # Convert the PDF to images (first page only)
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
        
        if not images:
            raise Exception("Failed to convert PDF to images")

        # Get the first page as an image
        first_page_image = images[0]

        # Save the image as PNG to an in-memory buffer (optional step, not necessary for QR decoding)
        png_buffer = io.BytesIO()
        first_page_image.save(png_buffer, format="PNG")
        png_buffer.seek(0)

        # Decode QR codes from the image
        decoded_objects = decode(first_page_image)
        if decoded_objects:
            # Extract data from the first QR code found
            qr_data = decoded_objects[0].data.decode("utf-8")
            print(f"QR Code Data Found: {qr_data}")
            return qr_data
        else:
            return None

    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise



def assign_evaluations(students, papers, trusted_evaluators, k):
    """
    Assigns papers to students for peer evaluation, ensuring:
    1. No student evaluates their own paper.
    2. Each paper is evaluated exactly k times.
    3. Trusted evaluators handle more papers based on their trust level.
    
    Parameters:
    - students: List of student IDs.
    - papers: List of paper objects with `uid` (owner ID) and `exam` attributes.
    - trusted_evaluators: Dictionary mapping student IDs to trust levels (0 to 1).
    - k: Number of evaluations required per paper.

    Returns:
    - assignments: Dictionary mapping students to their assigned papers.
    - paper_evaluations: Dictionary tracking the number of evaluations per paper.
    """
    # Initialize data structures
    assignments = {student: [] for student in students}
    paper_evaluations = {paper: 0 for paper in papers}
    student_workload = {student: 0 for student in students}

    # Calculate the maximum evaluations each student can handle
    max_evaluations = {student: k for student in students}
    for student, trust_level in trusted_evaluators.items():
        max_evaluations[student] += int(k * trust_level)

    # Create a pool of required evaluations
    evaluation_pool = []
    for paper in papers:
        for _ in range(k):
            evaluation_pool.append(paper)
    random.shuffle(evaluation_pool)

    # Assign evaluations while avoiding self-evaluation
    for paper in evaluation_pool:
        eligible_evaluators = [
            student for student in students
            if (student_workload[student] < max_evaluations[student] and
                paper not in assignments[student] and
                student != UIDMapping.objects.get(uid=paper.uid).user)
        ]

        if not eligible_evaluators:
            raise ValueError(f"Unable to assign paper {paper.uid} due to constraints.")

        evaluator = random.choice(eligible_evaluators)
        assignments[evaluator].append(paper)
        student_workload[evaluator] += 1
        paper_evaluations[paper] += 1

    # Validation and final correction pass
    for student, assigned_papers in assignments.items():
        for paper in assigned_papers:
            if student == getattr(paper, 'uid', None):  # Check for self-evaluation
                # Swap the paper with another student
                for other_student in students:
                    if (other_student != getattr(paper, 'uid', None) and
                        paper not in assignments[other_student] and
                        len(assignments[other_student]) < max_evaluations[other_student]):
                        # Perform the swap
                        assignments[student].remove(paper)
                        assignments[other_student].append(paper)
                        break
                else:
                    raise ValueError(f"Unable to resolve self-evaluation for paper {paper.uid}.")

    # Verify all papers are evaluated exactly k times
    for paper in papers:
        if paper_evaluations[paper] != k:
            raise ValueError(f"Paper {paper.uid} has {paper_evaluations[paper]} evaluations instead of {k}.")

    # Save PeerEvaluation objects
    for student, assigned_papers in assignments.items():
        subject = "Peer Evaluation Request"
        html_message = render_to_string(
            "email/send_evaluations.html",
            {
                "username": student.first_name,
                "evaluation_link": "https://pes.iitrpr.ac.in",
                "number_of_evaluations": len(assigned_papers)
            },
        )
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email="no-reply@evaluation-system.com",
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False)
        for paper in assigned_papers:
            new_eval = PeerEvaluation(
                document=paper,
                evaluator=student,
                exam=paper.exam,
                uid=paper.uid,
                student=UIDMapping.objects.get(uid=paper.uid).user,
                ticket=0
            )
            new_eval.save()

    return assignments, paper_evaluations



# NOTE: This function renders dashboard for all the roles
@login_required(login_url="/login/")
def index(request):

    # Handle login for Admin
    if request.user.is_superuser:
        courses = Course.objects.all()
        batches = Batch.objects.all()
        teachers = User.objects.filter(is_superuser=False, is_staff=True)
        batches_list = []

        for batch in batches:
            batches_list.append({
                'id':batch.id,
                'batch_id': batch.batch_id,
                'course_name': batch.course.name,
                'teacher': batch.teacher.username,
            })

        context = {
            'segment': 'index',
            'courses': courses,
            'batches': batches_list,
            'teachers': teachers,
            'counts': {
                'courses': len(courses),
                'batches': len(batches_list),
                'students': User.objects.filter(is_staff=False).count(),
                'teachers': User.objects.filter(is_staff=True).count() - 1
            }
        }
        html_template = loader.get_template('home/admin/index.html')
        return HttpResponse(html_template.render(context, request))
    
    # Handle login for Teacher
    elif request.user.is_staff:
        batches = Batch.objects.filter(teacher=request.user)

        batches_list = []
        for batch in batches:
            batches_list.append({
                'id': batch.id,
                'batch_id': batch.batch_id,
                'course_name': batch.course.name,
                'course_id': batch.course.course_id,
                'teacher': batch.teacher.username,
                'strength': StudentEnrollment.objects.filter(batch=batch, approval_status=True).count()
            })
        
        # Fetch students for these batches
        students_list = []
        tas = []
        for batch in batches:
            tas_for_batch = TeachingAssistantAssociation.objects.filter(batch=batch)
            students = StudentEnrollment.objects.filter(batch=batch, approval_status=True)
            ta = User.objects.filter(is_staff=True).first()
            for enrollment in students:
                incentives = Incentivization.objects.filter(student=enrollment.student, batch=batch).first()
                students_list.append({
                    'student_username': enrollment.student.username,
                    'student_email': enrollment.student.email,
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id,
                    'incentivization': round(incentives.rewards, 2) if incentives else 0
                })
            for ta in tas_for_batch:
                tas.append({
                    'ta_username': ta.teaching_assistant.username,
                    'ta_email': ta.teaching_assistant.email,
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id,
                    'ta_id': ta.id
                })

        context = {
            'segment': 'index',
            'batches': batches_list,
            'students': students_list,
            'tas': tas,
        }

        html_template = loader.get_template('home/teacher/index.html')
        return HttpResponse(html_template.render(context, request))
    
    # Handle login for Student and TA
    elif not request.user.is_staff or not request.user.is_superuser: # Student role

        enrolled_courses = StudentEnrollment.objects.filter(student=request.user).values_list('batch', flat=True)
        pending_evaluations = PeerEvaluation.objects.filter(evaluator=request.user, score="")
        batches = Batch.objects.all()
        tas = [{
            'batch': ta.batch.batch_id,
            'course': ta.batch.course.name,
            'ta_username': ta.teaching_assistant.username,
            'ta_email': ta.teaching_assistant.email,
        } for ta in TeachingAssistantAssociation.objects.filter(teaching_assistant=request.user)]
        batches_list = []
        topics = []
        for batch in batches:
            course = batch.course
            batches_list.append({
                "batchID": batch.id,
                'course_id': course.course_id,
                'batch': batch.batch_id,
                'name': course.name,
                'description': course.description,
                'is_public': course.is_public,
                'start_date': course.start_date,
                'end_date': course.end_date,
                'is_enrolled': batch.id in enrolled_courses,
                'is_accepted': batch.id in StudentEnrollment.objects.filter(student=request.user, approval_status=True).values_list('batch', flat=True)
            })
            topic = CourseTopic.objects.filter(batch=batch, date=datetime.now().date()).first()
            if topic:
                topics.append(topic)

        # Define the India timezone
        india_timezone = pytz.timezone('Asia/Kolkata')

        # Get the current time in IST
        current_time = timezone.now().astimezone(india_timezone)

        # Assuming all dates stored in the database are UTC and making them aware in the application.
        exams = Exam.objects.filter(batch__in=batches, completed=False)
        active_exams = []

        for exam in exams:
            # Ensure the exam date is timezone aware
            exam_date = timezone.make_aware(exam.date, timezone=pytz.UTC) if exam.date.tzinfo is None else exam.date
            
            # Convert exam date to IST
            exam_date_ist = exam_date.astimezone(india_timezone)
            
            # Calculate the expiration time
            expiration_time = exam_date_ist + timedelta(minutes=exam.duration)
            
            if exam_date_ist <= current_time <= expiration_time:
                exam.expiration_date = expiration_time
                active_exams.append(exam)

        counts = {
            "courses_enrolled": enrolled_courses.count(),
            "pending_evaluations": pending_evaluations.count(),
            "tas": len(tas),
            "active_exams": len(active_exams)  # Number of active exams in the current time window.
        }
        context = {'segment': 'index', 'courses': batches_list, 'counts': counts,
                   'exams': active_exams, 'topics': topics}
        html_template = loader.get_template('home/student/index.html')
        return HttpResponse(html_template.render(context, request))


# Invalid URL
@login_required(login_url="/login/")
def pages(request):
    context = {}
    
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@user_passes_test(is_superuser)
def course(request):

    # Create new course
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        description = request.POST.get('description')
        is_public = bool(request.POST.get('is_public'))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if course_name and start_date and end_date:
            try:
                Course.objects.create(
                    name=course_name,
                    description=description,
                    is_public=is_public,
                    start_date=start_date,
                    end_date=end_date,
                    course_id=course_id
                )
                messages.success(request, 'Course added successfully!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('home')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Delete a course
    elif request.method == 'DELETE':
        try:
            data = request.body.decode('utf-8')
            course_id = json.loads(data)['course_id']

            if not course_id:
                messages.error(request, 'Batch ID is required.')
                return redirect('home')

            course = Course.objects.get(id=course_id)
            course.delete()

            messages.success(request, 'Batch deleted successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('home')


    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')
    

@user_passes_test(is_superuser)
def batch(request):

    # Create new batch
    if request.method == 'POST':
        # Extract form data
        batch_name = request.POST.get('batchName')
        course_id = request.POST.get('batchCourse')
        teacher_username = request.POST.get('batchTeacher')

        if not batch_name or not course_id or not teacher_username:
            messages.error(request, 'All fields are required.')
            return redirect('home')

        try:
            # Fetch the course and teacher
            course = Course.objects.get(id=course_id)
            teacher = User.objects.get(username=teacher_username)

            # Create the batch
            Batch.objects.create(
                batch_id=batch_name,
                course=course,
                teacher=teacher
            )

            # Update the teacher's role and staff status
            teacher.is_staff = True
            teacher.save()

            messages.success(request, 'Batch added successfully!')
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
        except User.DoesNotExist:
            messages.error(request, 'Teacher not found.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('home')

    # Delete a batch
    elif request.method == 'DELETE':
        try:
            data = request.body.decode('utf-8')
            batch_id = json.loads(data)['batch_id']

            if not batch_id:
                messages.error(request, 'Batch ID is required.')
                return redirect('home')

            batch = Batch.objects.get(id=batch_id)
            batch.delete()

            messages.success(request, 'Batch deleted successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('home')


    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')


# Generate blank PDFs for students
def generate_student_pdf(student, exam, n_extra_pages):
    """Helper function to generate PDF for a single student"""
    pdf_files = []
    temp_files = []
    
    try:
        # Create QR Code
        qr = qrcode.QRCode(version=1, box_size=4, border=4)
        qr.add_data(student.uid)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")
        
        # Save QR code to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            qr_img.save(tmpfile.name)
            temp_files.append(tmpfile.name)
            
            # Generate first page with all details and blank page
            pdf = FPDF()
            
            # First page with details
            pdf.add_page()
            
            # Add header
            pdf.set_font("Arial", "B", size=16)
            pdf.cell(200, 10, txt=f"Answer Sheet", ln=True, align='C')
            
            # Move to position for table
            pdf.set_y(40)
            
            # QR code on the left
            pdf.image(tmpfile.name, x=10, y=10, w=25, h=25)
            
            # Details on the right
            x_start = 80
            y_start = 40
            line_height = 10
            
            # Set position for details
            pdf.set_xy(x_start, y_start)
            
            # Add student details in table format
            details = [
                ('Name', f"{student.user.first_name} {student.user.last_name}"),
                ('Username', student.user.username),
                ('Batch', exam.batch.batch_id),
                ('Date', exam.date.strftime('%Y-%m-%d')),
                ('UID', student.uid)
            ]
            
            for label, value in details:
                # Label (bold)
                pdf.set_font("Arial", "B", size=12)
                pdf.cell(30, line_height, txt=label + ":", align='L')
                
                # Value (regular)
                pdf.set_font("Arial", "", size=12)
                pdf.cell(70, line_height, txt=value, ln=True)
                
                # Move to next line
                pdf.set_x(x_start)
            
            # Add blank page
            pdf.add_page()
            
            # Save first two pages (details + blank)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_tmpfile:
                pdf.output(pdf_tmpfile.name)
                pdf_files.append(pdf_tmpfile.name)
                temp_files.append(pdf_tmpfile.name)
            
            # Generate additional pages with only QR code
            pdf = FPDF()
            for _ in range(n_extra_pages):
                pdf.add_page()
                pdf.image(tmpfile.name, x=10, y=10, w=25, h=25)
            
            # Save additional pages
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_tmpfile:
                pdf.output(pdf_tmpfile.name)
                pdf_files.append(pdf_tmpfile.name)
                temp_files.append(pdf_tmpfile.name)
            
            return pdf_files, temp_files
            
    except Exception as e:
        # Clean up any created temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass
        raise e
    

# Route for downloading the blank PDFs
@user_passes_test(is_staff)
def download_answer_sheets(request):

    if request.method == 'POST':
        try:
            # Get the exam and number of extra pages
            exam_id = request.POST.get('exam_id')
            n_extra_pages = int(request.POST.get('n_extra_pages', 5))  # Default to 1 extra page

            exam = Exam.objects.get(id=exam_id)
            students = UIDMapping.objects.filter(exam=exam)
            
            if not students.exists():
                messages.error(request, 'No students found for this exam.')
                return redirect('home')
            
            # Create a BytesIO object to store the final PDF
            output = BytesIO()
            merger = PdfMerger()
            
            # Keep track of all temporary files
            all_temp_files = []
            
            # Generate PDFs for each student
            for student in students:
                pdf_files, temp_files = generate_student_pdf(student, exam, n_extra_pages)
                for pdf_file in pdf_files:
                    merger.append(pdf_file)
                all_temp_files.extend(temp_files)
                all_temp_files.extend(pdf_files)
            
            # Write the merged PDF to BytesIO
            merger.write(output)
            merger.close()
            
            # Clean up temporary files
            for temp_file in all_temp_files:
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            
            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{exam.batch.batch_id}_answer_sheets.pdf"'
            
            return response
            
        except Exception as e:
            print(e)
            messages.error(request, f'Error generating PDFs: {str(e)}')
            return redirect('examination')
    
    messages.error(request, 'Invalid request method.')
    return redirect('home')


# Enrollment of student
def enrollment(request):

    if request.method == 'POST':     
        try:   
            data = request.body.decode('utf-8')
            print(data)
            batch_id = int(json.loads(data)['batch_id'])
            role = json.loads(data)['role']
            if role == "TA":
                username = str(json.loads(data)['student_username'])
                action = json.loads(data)['student_action']
                username = User.objects.get(email=username)
                studentenrollment = StudentEnrollment.objects.filter(batch_id=batch_id, student__username=username).first()
                if studentenrollment:
                    if action == 1:
                        print(action == 1)
                        studentenrollment.approval_status = True
                        studentenrollment.update()
                        messages.success(request, 'Student approved successfully!')
                        print("Approved")
                    elif action == 0:
                        studentenrollment.delete()
                        messages.error(request, 'Student rejected successfully!')
                        print("Rejected")
                else:
                    messages.error(request, 'Student not found in the selected batch.')
                    print("Not found")
                return redirect('home')
        except Exception as e:
            pass
        batch_id = int(request.POST.get('batch_id'))
        batch = Batch.objects.get(id=batch_id)
        student_username = request.user.username
        if course and student_username:
            try:
                student = User.objects.get(username=student_username)

                enrolment = StudentEnrollment.objects.filter(student_id=student.id, batch_id=batch.id).first()

                if enrolment:
                    if enrolment.approval_status:
                        messages.error(request, 'Student already enrolled in this course.')
                        return redirect('home')
                    else:
                        enrolment.delete()
                        messages.error(request, 'Student has not been approved by the teacher.')
                        return redirect('home')
                else:
                    StudentEnrollment.objects.create(
                        student=student,
                        course=batch.course,
                        batch=batch
                    )
                    messages.success(request, 'Student enrollment requested!')
                    return redirect('home')

            except Batch.DoesNotExist:
                messages.error(request, 'Batch not found.')
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, 'Student not found.')
                return redirect('home')
        else:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('home')
    
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')
    

@login_required
def ta_hub(request):

    # Fetch data for TA hub
    if request.method == 'GET':
        if request.user.is_ta:
            batches = Batch.objects.filter(ta_associations__teaching_assistant=request.user)
            peerevaluations = PeerEvaluation.objects.filter(exam__batch__in=batches).filter(Q(score="") | Q(ticket__gt=0))
            topics = CourseTopic.objects.filter(batch__in=batches).order_by('-date')[:5]

            tas = [{
                'id': ta.id,
                'batch': ta.batch,
                'batch_id': ta.batch.id,
                'course': ta.batch.course.name,
                'start_date': ta.batch.course.start_date,
                'instructor': f"{ta.batch.teacher.first_name} {ta.batch.teacher.last_name}",
                'instructor_email': ta.batch.teacher.email,
                'students': [
                    {
                        "name": f"{student.student.first_name} {student.student.last_name}",
                        "username": student.student.username,
                        "email": student.student.email
                    }
                    for student in StudentEnrollment.objects.filter(batch=ta.batch.id, approval_status=False).order_by('approval_status')
                ],
            } for ta in TeachingAssistantAssociation.objects.filter(teaching_assistant=request.user)]
            return render(request, 'home/student/ta_hub.html', {'evaluations': peerevaluations, 'batches': batches, 'ta': tas, 'is_ta': len(tas) > 0, 'topics': topics})
        else:
            return redirect('home')

    # Associate Teaching associate with batch
    if request.method == 'POST':
        batch_id = request.POST.get('batch_id')
        ta_username = request.POST.get('teachingAssistantName')
        batch = Batch.objects.get(id=batch_id)
        ta = User.objects.filter(Q(email=ta_username) | Q(username=ta_username)).first()
        if not ta:
            messages.error(request, 'TA not found.')
            return redirect('home')
        
        if request.user.is_teacher():
            try:
                TeachingAssistantAssociation.objects.create(
                    batch=batch,
                    teaching_assistant=ta
                )
                messages.success(request, 'TA assigned successfully!')
                return redirect('home')
            except IntegrityError:
                messages.error(request, 'TA already assigned to this batch.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'You are not authorized to perform this operation.')
    
    return redirect('home')


@user_passes_test(is_staff)
def examination(request):

    if request.method == 'GET':
        if request.user.is_staff:
            batches = Batch.objects.filter(teacher=request.user)
            batch_data = []
            exams_list = []
            chart_data_list = {}
            archive = {}

            for batch in batches:
                archived_exams = Exam.objects.filter(batch=batch, completed=True).order_by('-date')
                exams = Exam.objects.filter(batch=batch, completed=False).first()

                # Add analytics for archived exams
                archive[batch.course.name + " " + batch.batch_id] = []
                for archived_exam in archived_exams:
                    archived_exam.document_count = Documents.objects.filter(exam=archived_exam).count()
                    evaluations = PeerEvaluation.objects.filter(exam=archived_exam)
                    student_scores = {}

                    # Adjust student scores by dividing by archived_exam.k
                    for evaluation in evaluations:
                        if evaluation.student_id not in student_scores:
                            student_scores[evaluation.student_id] = 0
                        student_scores[evaluation.student_id] += evaluation.total / archived_exam.k

                    # Define bins for score histogram
                    max_marks = archived_exam.max_scores  # Total maximum marks
                    bin_count = 10
                    score_bins = np.linspace(0, max_marks, bin_count + 1)  # Create score bins

                    # Define bins for percentage pie chart
                    percentage_bins = np.linspace(0, 100, bin_count + 1)  # Percentage bins

                    # Initialize scores list for histogram
                    histogram_data = {
                        'labels': [0 for _ in range(len(score_bins) - 1)],
                        'values': [f"{int(score_bins[i])}-{int(score_bins[i + 1])}" for i in range(len(score_bins) - 1)],
                    }

                    # Initialize percentage list for pie chart
                    percentage_data = {
                        'labels': [0 for _ in range(len(percentage_bins) - 1)],
                        'values': [f"{int(percentage_bins[i])}%-{int(percentage_bins[i + 1])}%" for i in range(len(percentage_bins) - 1)],
                    }

                    # Distribute scores into bins for histogram
                    for student_id, score in student_scores.items():
                        for i in range(len(score_bins) - 1):
                            if score_bins[i] <= score < score_bins[i + 1]:
                                histogram_data['labels'][i] += 1
                                break

                    # Distribute percentages into bins for pie chart
                    for student_id, score in student_scores.items():
                        percentage = (score / max_marks) * 100  # Convert score to percentage
                        for i in range(len(percentage_bins) - 1):
                            if percentage_bins[i] <= percentage < percentage_bins[i + 1]:
                                percentage_data['labels'][i] += 1
                                break

                    # Combine both datasets
                    archived_exam.graphs = {
                        'histogram': histogram_data,
                        'pie_chart': percentage_data,
                    }
                    archive[batch.course.name + " " + batch.batch_id].append(archived_exam)


                if exams:
                    exams.document_count = Documents.objects.filter(exam=exams).count()
                    evaluations = PeerEvaluation.objects.filter(exam=exams)
                    student_scores = {}

                    # Adjust student scores by dividing by exams.k
                    for evaluation in evaluations:
                        if evaluation.student_id not in student_scores:
                            student_scores[evaluation.student_id] = 0
                        student_scores[evaluation.student_id] += evaluation.total / exams.k

                    # Define bins for score histogram
                    max_marks = exams.max_scores  # Total maximum marks
                    bin_count = 10
                    score_bins = np.linspace(0, max_marks, bin_count + 1)  # Create score bins

                    # Define bins for percentage pie chart
                    percentage_bins = np.linspace(0, 100, bin_count + 1)  # Percentage bins

                    # Initialize scores list for histogram
                    histogram_data = {
                        'labels': [0 for _ in range(len(score_bins) - 1)],
                        'values': [f"{int(score_bins[i])}-{int(score_bins[i + 1])}" for i in range(len(score_bins) - 1)],
                    }

                    # Initialize percentage list for pie chart
                    percentage_data = {
                        'labels': [0 for _ in range(len(percentage_bins) - 1)],
                        'values': [f"{int(percentage_bins[i])}%-{int(percentage_bins[i + 1])}%" for i in range(len(percentage_bins) - 1)],
                    }

                    # Distribute scores into bins for histogram
                    for student_id, score in student_scores.items():
                        for i in range(len(score_bins) - 1):
                            if score_bins[i] <= score < score_bins[i + 1]:
                                histogram_data['labels'][i] += 1
                                break

                    # Distribute percentages into bins for pie chart
                    for student_id, score in student_scores.items():
                        percentage = (score / max_marks) * 100  # Convert score to percentage
                        for i in range(len(percentage_bins) - 1):
                            if percentage_bins[i] <= percentage < percentage_bins[i + 1]:
                                percentage_data['labels'][i] += 1
                                break

                    # Combine both datasets
                    exams.graphs = {
                        'histogram': histogram_data,
                        'pie_chart': percentage_data,
                    }

                    exams_list.append(exams)
                batch_data.append({'batch': batch, 'exams': exams})
            
            return render(request, 'home/teacher/examination.html', {
                'batch_data': batch_data,
                'exams': exams_list,
                'archive': archive,  # Include archive in the context
            })


    elif request.method == 'POST':
        uploaded_file = request.FILES.get("schema_file")
        
        if not uploaded_file:
            messages.error(request,'No schema uploaded')
        # if uploaded_file.content_type != "application/pdf":
        #     messages.error(request,'Only PDF upload allowed')
        try:
            
            data = request.POST
            batch_id = int(data['batch_id'])
            exam_date = datetime.fromisoformat(data["exam_date"])
            exam_duration = int(data['duration'])
            num_que = int(data["num_que"])
            max_marks = int(data["max_marks"])
            k = int(data['k'])
            students_in_batch = StudentEnrollment.objects.filter(batch_id=batch_id, approval_status= True)
            new_exam = Exam.objects.update_or_create(batch_id=batch_id,
                                                     completed=False,
                                                        defaults={
                                                            'date': exam_date,
                                                            'duration': exam_duration,
                                                            'number_of_questions': num_que,
                                                            'max_scores': max_marks,
                                                            'k': k,
                                                            'total_students': len(students_in_batch),
                                                            'completed': False,
                                                            'solutions': f"{exam_date}_{batch_id}.pdf"
                                                        })
            pdf_content = uploaded_file.read()
            
            
            with open(f"apps/static/documents/{exam_date}_{batch_id}.pdf","wb") as f:
                f.write(pdf_content)
            
            if new_exam[1]:
                messages.success(request, 'Exam updated successfully!')
            else:
                messages.success(request, 'Exam created successfully!')
            for student in students_in_batch:
                UIDMapping.objects.update_or_create(user=student.student,
                                                    exam=new_exam[0],
                                                    defaults={'uid': generate_random_text()})
        except Exception as e:
            print(e)
            messages.error(request, f'An error occurred: {str(e)}')
        return redirect('examination')


    elif request.method == 'DELETE':
        if request.user.is_staff:
            data = request.body.decode('utf-8')
            if data:
                try:
                    exam_id = json.loads(data)['exam_id']
                    exam = Exam.objects.get(id=exam_id)
                    exam.delete()
                    return redirect('examination')
                    messages.success(request, 'Exam deleted successfully!')
                except json.JSONDecodeError:
                    print(request, 'Invalid JSON data.')
                except Exam.DoesNotExist:
                    print(request, 'Exam not found.')
                except Exception as e:
                    print(request, f'An error occurred: {str(e)}')
            else:
                pass
            return redirect('examination')


    elif request.method == 'PUT':
        if request.user.is_staff:
            data = request.body.decode('utf-8')
            if data:
                try:
                    exam_id = json.loads(data)['exam_id']
                    exam = Exam.objects.get(id=exam_id)
                    students = UIDMapping.objects.filter(exam=exam)
                    for student in students:
                        subject = "Peer Evaluation Results"
                        html_message = render_to_string(
                            "email/results_available.html",
                            {
                                "username": student.user.first_name,
                                "evaluation_link": "https://pes.iitrpr.ac.in",
                                "date": exam.date.strftime('%d/%m/%Y'),
                                "course": exam.batch.course.name,
                                "batch": exam.batch.batch_id
                            },
                        )
                        plain_message = strip_tags(html_message)
                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email="no-reply@evaluation-system.com",
                            recipient_list=[student.user.email],
                            html_message=html_message,
                            fail_silently=False)
                    exam.completed = True
                    exam.save()
                except json.JSONDecodeError:
                    print(request, 'Invalid JSON data.')
                except Exam.DoesNotExist:
                    print(request, 'Exam not found.')
                except Exception as e:
                    print(request, f'An error occurred: {str(e)}')
            else:
                print(request, 'No data provided.')
            return redirect('examination')


    else:
        print(request, 'Invalid request method.')
        return 


# def handle_post_request(request):
#     if request.user.is_staff:
#         data = json.loads(request.body.decode('utf-8'))
#         exam_id = data['exam_id']
#         exam_instance = Exam.objects.get(id=exam_id)

#         if data['flag'] == 0:
#             student_enrollment = [uid.user for uid in UIDMapping.objects.filter(exam=exam_instance)]
#             papers = list(Documents.objects.filter(exam=exam_instance))
#             k = exam_instance.k
#             incentives = {}
#             success = False
#             attempts = 0
#             max_attempts = 10

#             def assign_task():
#                 nonlocal success, attempts
#                 while not success and attempts < max_attempts:
#                     try:
#                         # Attempt to assign evaluations
#                         assign_evaluations(student_enrollment, papers, incentives, k)
#                         success = True  # Exit loop if successful
#                     except Exception as e:
#                         # Log the exception and retry
#                         print(f"Error: {e}. Retrying... (Attempt {attempts + 1}/{max_attempts})")
#                         attempts += 1
#                         time.sleep(1)

#                 if not success:
#                     # Log or handle failure
#                     print('Failed to assign evaluations after multiple attempts.')
#                 else:
#                     # Update the exam instance once successful
#                     exam_instance.evaluations_sent = True
#                     exam_instance.save()

#             thread = threading.Thread(target=assign_task)
#             thread.start()
#             messages.success(request, 'Evaluation assignment is being processed in the background.')
#             return redirect('examination')

#         elif  data['flag'] == 1:
#             data = json.loads(request.body.decode('utf-8'))
#             exam_instance = Exam.objects.get(id=data['exam_id'])
#             flag_evaluations_with_high_std(exam_instance, request)
#             return redirect('examination')

@login_required
def peer_evaluation(request):

    if request.method == 'GET':
        peerevaluations = PeerEvaluation.objects.filter(evaluator=request.user, exam__completed=False)
        results = PeerEvaluation.objects.filter(student=request.user, exam__completed=True)
        final_results = {}
        for result in results:
            course = result.exam.batch.course.name
            batch_id = result.exam.batch.batch_id
            exam_id = result.exam.id
            max_scores = result.exam.max_scores
            score = sum(result.get_score)

            if exam_id not in final_results:
                final_results[exam_id] = {
                    'course': course,
                    'batch_id': batch_id,
                    'date': result.exam.date.strftime('%d/%m/%Y'),
                    'total_score': 0,
                    'count': 0,
                    'max_scores': max_scores,
                    'evaluations': []
                }

            final_results[exam_id]['total_score'] += score
            final_results[exam_id]['count'] += 1
            final_results[exam_id]['evaluations'].append(result)

        for exam_id, data in final_results.items():
            data['score'] = data['total_score'] / data['count'] if data['count'] != 0 else 0

        final_results = [final_results[i] for i in final_results.keys()]

        return render(request, 'home/student/peer_evaluation.html', {'evaluations': peerevaluations,
                                                                     'is_ta': TeachingAssistantAssociation.objects.filter(teaching_assistant=request.user) != None,
                                                                     'results': final_results})


    if request.method == 'POST':
        if request.user.is_staff:
            data = json.loads(request.body.decode('utf-8'))
            exam_id = data['exam_id']
            exam_instance = Exam.objects.get(id=exam_id)
            if (data['flag']) == 0:
                student_enrollment = [uid.user for uid in UIDMapping.objects.filter(exam=exam_instance)]
                papers = list(Documents.objects.filter(exam=exam_instance))
                k = exam_instance.k
                incentives = {}
                success = False
                attempts = 0
                max_attempts = 10
                def assign_task():
                    nonlocal success, attempts
                    while not success and attempts < max_attempts:
                        try:
                            # Attempt to assign evaluations
                            assign_evaluations(student_enrollment, papers, incentives, k)
                            success = True  # Exit loop if successful
                        except Exception as e:
                            # Log the exception and retry
                            print(f"Error: {e}. Retrying... (Attempt {attempts + 1}/{max_attempts})")
                            attempts += 1
                            time.sleep(1)
                assign_thread = threading.Thread(target=assign_task)
                assign_thread.start()
                assign_thread.join()
                if not success:
                    messages.error(request, 'Failed to assign evaluations after multiple attempts.')
                    return redirect('examination')
                        
                exam_instance.evaluations_sent = True
                exam_instance.save()
                return redirect('examination')
            else:
                flag_evaluations_with_high_std(exam_instance, request)
                return redirect('examination')


    else:
        return redirect('home')


@login_required
def student_eval(request):

    if request.method == "POST":
        try:
            form_data = request.POST
            document_id = int(form_data.get('current_evaluation_id'))
            evaluation = PeerEvaluation.objects.get(id=document_id)
            number_of_questions = evaluation.exam.number_of_questions
            evaluations = [int(form_data.get(f'question-{i}', 0)) for i in range(1, number_of_questions + 1)]
            is_ta_evaluating = form_data.get('is_ta_evaluating') == 'true'
            if request.user.is_ta:
                incentive = Incentivization.objects.filter(student=evaluation.evaluator, batch=evaluation.exam.batch).first()
                total_exams = UIDMapping.objects.filter(exam__batch=evaluation.exam.batch).count()
                alpha = 0.1
                exam_count = PeerEvaluation.objects.filter(student=evaluation.evaluator, exam__batch=evaluation.exam.batch, score__isnull=False).values('exam_id').distinct().count()
                reward = (1 if evaluation.score != "" and (eval(evaluation.score) == evaluations) else -1) * (1 / (1 + math.exp(-alpha * exam_count))) / total_exams
                if evaluation.score != "" and (eval(evaluation.score) == evaluations):
                    evaluation.evaluator = request.user
                if incentive:
                    incentive.rewards = min(incentive.rewards + reward, 1.0)
                    incentive.exam_count = exam_count
                else:
                    incentive = Incentivization(
                        student=evaluation.evaluator,
                        batch=evaluation.exam.batch,
                        rewards=reward,
                        exam_count=1
                    )
                if is_ta_evaluating and not request.user.is_ta:
                    incentive.rewards = 0
                incentive.save()

            feedback = [form_data.get(f'feedback-{i}', '').strip() for i in range(1, number_of_questions + 1)]
            evaluation.feedback = feedback
            evaluation.score = str(evaluations)
            evaluation.ticket = 0
            evaluation.save()
            messages.success(request, 'Evaluation submitted successfully!')
            return redirect('peer_eval')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return redirect('peer_eval')


@login_required
def upload_evaluation(request):


    if request.method == "POST":
        uploaded_files = request.FILES.getlist("evaluationfile")
        exam_id = request.POST.get("exam_id")

        if not uploaded_files:
            return redirect('examination')

        try:
            try:
                exam = Exam.objects.get(id=exam_id)
            except Exam.DoesNotExist:
                if request.user.is_teacher:
                    messages.error(request, 'Exam not found.')
                    return redirect('examination')
                else:
                    return redirect('home')

            # Limit students to one file
            if request.user.is_student():
                if len(uploaded_files) > 1:
                    return redirect('home')
                
                uploaded_file = uploaded_files[0]
                if uploaded_file.content_type != "application/pdf":
                    return redirect('home')

                pdf_content = uploaded_file.read()
                qr_content = convert_pdf_to_image_and_decode_qr(pdf_content)
                if not qr_content:
                    return redirect('home')
                final_filename = f"{qr_content}.pdf"

                uid_mapping = UIDMapping.objects.filter(user=request.user, exam=exam, uid=qr_content).first()
                if not uid_mapping:
                    print("No UID Mappings found")
                    return redirect('examination')

                document = Documents.objects.filter(uid=qr_content).first()
                if not document:
                    Documents.objects.create(
                        uid=qr_content,
                        exam=exam,
                        document=final_filename,
                        uploaded_by=request.user
                    )
                   
                    with open(f"apps/static/documents/{final_filename}", "wb") as f:
                        f.write(pdf_content)
                messages.success(request, 'Evaluation uploaded successfully!')
                return redirect('home')

            elif request.user.is_teacher():
                for uploaded_file in uploaded_files:
                    if uploaded_file.content_type != "application/pdf":
                        return redirect('examination')
                    
                    # Process each file
                    pdf_content = uploaded_file.read()
                    qr_content = convert_pdf_to_image_and_decode_qr(pdf_content)
                    if not qr_content:
                        return redirect('examination')
                    
                    final_filename = f"{qr_content}.pdf"
                    print(final_filename)

                    uid_mapping = UIDMapping.objects.filter(exam=exam, uid=qr_content).first()
                    if not uid_mapping:
                        continue  # Skip files with no valid UID mapping
                    
                    # Create or update document
                    Documents.objects.update_or_create(
                        uid=qr_content,
                        exam=exam,
                        defaults={
                            'document': final_filename,
                            'uploaded_by': request.user
                        }
                    )
                    with open(f"apps/static/documents/{final_filename}", "wb") as f:
                        f.write(pdf_content)
                messages.success(request, f'{len(uploaded_files)} Evaluations uploaded successfully!')
                return redirect('examination')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, "home/student/peer_evaluation.html",
                          {"error": f"An error occurred while processing the files: {str(e)}"})

    print("Invalid request method.")
    return render(request, "home/student/peer_evaluation.html")

def export_evaluations_to_csv(request, exam_id):

    # Fetch all evaluations with the required fields
    evaluations = PeerEvaluation.objects.filter(exam_id=int(exam_id)).values(
        'evaluator_id', 'evaluated_on', 'document_id', 'student_id', 
        'exam_id', 'feedback', 'ticket', 'score'
    )
    exam = Exam.objects.get(id=exam_id)

    # Convert the queryset to a DataFrame
    df_evaluations = pd.DataFrame(evaluations)

    # Handle empty data
    if df_evaluations.empty:
        return HttpResponse("No evaluations available.", content_type="text/plain")

    # Convert timezone-aware datetimes to timezone-unaware
    for col in ['evaluated_on', 'deadline']:
        if col in df_evaluations.columns:
            df_evaluations[col] = df_evaluations[col].apply(
                lambda dt: dt.replace(tzinfo=None) if is_aware(dt) else dt
            )

    # Helper function to safely parse and calculate average scores
    def calculate_avg_scores(scores):
        try:
            # Parse scores into lists of numbers and calculate the average
            score_lists = [ast.literal_eval(score) for score in scores if isinstance(score, str)]
            flattened_scores = [item for sublist in score_lists for item in sublist]
            return sum(flattened_scores) if flattened_scores else 0
        except (ValueError, SyntaxError):
            # Return 0 if parsing fails
            return 0

    # Prepare 'Marks Distribution' sheet
    df_avg_marks = df_evaluations.groupby(['document_id']).agg({'score': calculate_avg_scores}).reset_index()
    df_avg_marks.rename(columns={'score': 'avg_marks'}, inplace=True)

    # Add student details using UIDMapping and Documents models
    student_data = []
    for _, row in df_avg_marks.iterrows():
        try:
            # Get the document details
            doc = Documents.objects.get(id=row['document_id'])
            # Get the UIDMapping for the document's UID and exam
            uid_mapping = UIDMapping.objects.get(uid=doc.uid, exam=doc.exam)
            # Fetch the corresponding user
            student = uid_mapping.user
            student_data.append({
                'Document ID': row['document_id'],
                'Student Name': f"{student.first_name} {student.last_name} ({student.username})",
                'Average Marks': row['avg_marks']/exam.k
            })
        except Documents.DoesNotExist:
            student_data.append({
                'Document ID': row['document_id'],
                'Student Name': 'Unknown',
                'Average Marks': row['avg_marks']/exam.k
            })
        except UIDMapping.DoesNotExist:
            student_data.append({
                'Document ID': row['document_id'],
                'Student Name': 'UID Mapping Not Found',
                'Average Marks': row['avg_marks']/exam.k
            })

    # Convert to DataFrame for Sheet 1
    df_sheet1 = pd.DataFrame(student_data)

    filename = f"{exam.date.strftime('%Y-%m-%d')}_{exam.batch.course.name}_{exam.batch.batch_id}"
    # Generate Excel file with the processed data
    with pd.ExcelWriter(f'{filename}.xlsx', engine='openpyxl') as writer:
        # Write 'Marks Distribution' sheet
        df_sheet1.to_excel(writer, sheet_name='Marks Distribution', index=False)
        # Write raw evaluations data to another sheet
        df_evaluations.to_excel(writer, sheet_name='Evaluations', index=False)

    # Read the file and prepare response
    with open(f'{filename}.xlsx', 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
    os.remove(f'{filename}.xlsx')

    return response


@user_passes_test(is_ta)
def topic(request):

    if request.method == "POST":
        data = request.POST
        batch = Batch.objects.filter(id=data.get("course")).first()
        topic_name = data.get("topic_name")
        topic_description = data.get("description")
        todays_topic = CourseTopic.objects.filter(course=batch.course, batch=batch, date=datetime.now().date()).first()

        if topic_name and topic_description:
            if todays_topic:
                todays_topic.topic = topic_name
                todays_topic.description = topic_description
                todays_topic.date = datetime.now().date()
                todays_topic.save()
                return redirect('ta_hub')
            else:
                topic = CourseTopic.objects.create(
                    course=batch.course,
                    batch=batch,
                    topic=topic_name,
                    description=topic_description
                )
                topic.save()
            return redirect('ta_hub')

    return redirect('ta_hub')


@login_required
def llm_answer(request):

    if request.method == "POST":
        data = request.POST
        topic = data.get('todaysTopic')
        topic = CourseTopic.objects.filter(id=topic).first()
        lectureTakeaways = data.get('lectureTakeaways')
        exploreMore = data.get('exploreMore')
        llmevaluation = LLMEvaluation.objects.filter(Topic=topic, student=request.user).first()

        if llmevaluation:
            return redirect('home')
         
        if topic and lectureTakeaways and exploreMore:
            attempts = 0
            max_attempts = 5
            success = False
            while not success and attempts < max_attempts:
                try:
                    def evaluate_task():
                        evaluation = evaluate_answers(topic.topic, lectureTakeaways, exploreMore, topic.description)
                        LLMEvaluation.objects.create(
                            answer=evaluation['answers'],
                            feedback=evaluation['feedback'],
                            score=evaluation['scores'],
                            ai=evaluation['ai_scores'],
                            aggregate=evaluation['aggregate_score'],
                            date=topic.date,
                            Topic=topic,
                            student=request.user
                        )
                        incentive = Incentivization.objects.filter(student=request.user, batch=topic.batch).first()
                        total_exams = CourseTopic.objects.filter(batch=topic.batch).count()
                        exam_count = LLMEvaluation.objects.filter(student=request.user, Topic__batch=topic.batch).count()
                        alpha = 0.01
                        incremental_reward = (1 / (1 + math.exp(-alpha * exam_count))) / total_exams
                        if incentive:
                            incentive.rewards += incremental_reward
                            incentive.exam_count = exam_count
                            incentive.save()
                        else:
                            Incentivization.objects.create(
                                student=request.user,
                                batch=topic.batch,
                                rewards=incremental_reward,
                                exam_count=1
                            )

                    evaluation_thread = threading.Thread(target=evaluate_task)
                    evaluation_thread.start()
                    evaluation_thread.join()
                    success = True
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise e
            return redirect('home')
        else:
            return redirect('home')
    
    else:
        return redirect('home')
    


@csrf_exempt
def download_online_eval(request):
    if request.method == "POST":
        batch_id = request.POST.get("batch_id")
        print("Received Batch ID:", batch_id)  # Debugging

        if not batch_id:
            return JsonResponse({"error": "Batch ID is missing."}, status=400)

        try:
            batch_id = int(batch_id)  # Convert batch_id to integer
        except ValueError:
            return JsonResponse({"error": "Invalid Batch ID format."}, status=400)

        batch = Batch.objects.filter(id=batch_id).first()
        print("Fetched Batch:", batch)  # Debugging

        if not batch:
            return JsonResponse({"error": "Invalid Batch ID."}, status=404)

        evaluations = LLMEvaluation.objects.filter(Topic__batch=batch)
        print("Evaluations Found:", evaluations.exists())  # Debugging

        if not evaluations.exists():
            return JsonResponse({"error": "No evaluations found for this batch."}, status=404)

        # Convert evaluations to DataFrame
        data = [
            {
                "Evaluated On": eval.date.strftime("%Y-%m-%d"),
                "Student": eval.student.first_name + " " + eval.student.last_name + " (" + eval.student.username + ")",
                "Topic": eval.Topic.topic,
                "answer": eval.answer,
                "Feedback": eval.feedback,
                "AI": eval.ai,
                "Score": eval.score,
            }
            for eval in evaluations
        ]

        df = pd.DataFrame(data)

        # Generate Excel file
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="Online_Evaluation_Batch_{batch.id}.xlsx"'

        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        return response

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)  # Ensure only teachers or admins can remove TAs
def remove_ta(request):
    if request.method == 'POST':
        ta_association_id = request.POST.get('ta_association_id')
        # Step 1: Check if ID is provided
        if not ta_association_id:
            messages.error(request, "No TA ID provided.")
            return redirect('home')
        try:
            ta_association = get_object_or_404(TeachingAssistantAssociation, id=int(ta_association_id))
            ta_association.delete()
            messages.success(request, "TA removed successfully.")
        except ValueError:
            messages.error(request, "Invalid TA ID.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect('home')

    
@login_required
def change_password(request):

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change
            messages.success(request, "Your password has been changed successfully.")
            return render(request,'home/profile.html')  # Redirect to profile or home
    else:
        form = CustomPasswordChangeForm(user=request.user)

    messages.error(request, "Please input valid inputs.")
    return render(request,'home/profile.html')


def fetch_document(request, file_name):
    file_obj = Documents.objects.filter(file__icontains=file_name).first()
    if file_obj:
        file_path = file_obj.file.path
        with open(file_path, 'rb') as file:
            # Prepare the response with the file content
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={file_name}'
            return response
    

@login_required
def documentation(request):

    if request.method == "GET":
        if request.user.is_student():
            return render(request, 'documentation/student.html')
        else:
            return render(request, 'documentation/teacher.html')
        
def generate_password(length):
    MAX_LEN = length

    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']
    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']
    SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '/', '|', '~', '>', 
            '*', '(', ')', '<']

    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS

    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)

    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    for x in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)

        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)

    password = ""
    for x in temp_pass_list:
            password = password + x
            
    return password


def send_email_async(subject, plain_message, html_message, recipient_list):
    """Send email asynchronously using threading."""
    def send():
        send_mail(
            subject=subject,
            message=plain_message,
            from_email="no-reply@evaluation-system.com",
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    thread = threading.Thread(target=send)
    thread.start()

from django.contrib.auth import authenticate, login
from apps.authentication.forms import LoginForm, SignUpForm, PasswordResetForm

def bulk_register_users(request):
    msg = None
    success = False

    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        df = pd.read_csv(csv_file)

        created_users = []
        failed_users = []
        skipped_users = []

        batch_id = request.POST.get("batch_id")
        try:
            batch = Batch.objects.get(batch_id=batch_id)
        except Batch.DoesNotExist:
            return redirect('home')

        for index, row in df.iterrows():
            try:
                username = row["email"].split("@")[0]

                # Check if user already exists
                user = User.objects.filter(username=username).first()
                if user:
                    # Check if user is already enrolled in the batch
                    if StudentEnrollment.objects.filter(student=user, batch=batch, course=batch.course, approval_status=True).exists():
                        skipped_users.append(username)
                        continue
                    elif StudentEnrollment.objects.filter(student=user, batch=batch, course=batch.course, approval_status=False).exists():
                        existing = StudentEnrollment.objects.get(student=user, batch=batch, course=batch.course)
                        existing.approval_status = True
                        existing.update()
                        created_users.append(username)
                    else:
                        StudentEnrollment.objects.create(student=user, batch=batch, course=batch.course, approval_status=True)
                        created_users.append(username)                      

                else:
                    data = {
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "username": username,
                        "email": row["email"],
                        "is_staff": False,
                    }
                    password = generate_password(10)
                    data["password1"] = password
                    data["password2"] = password
                    print(row["first_name"])

                    # Create the form instance
                    form = SignUpForm(data)
                    if form.is_valid():
                        form.save()
                        user = authenticate(username=username, password=password)

                        if user and data["is_staff"]:
                            user.is_staff = True
                            user.save()

                        created_users.append(username)

                        # Send email notification asynchronously
                        email_template = "email/new_account.html"
                        subject = "Welcome to Peer Evaluation"
                        html_message = render_to_string(
                            email_template,
                            {
                                "name": data["first_name"],
                                "username": username,
                                "password": password,
                                "evaluation_link": "https://pes.iitrpr.ac.in",
                            },
                        )
                        plain_message = strip_tags(html_message)
                        send_email_async(subject, plain_message, html_message, [data["email"]])
                    else:
                        failed_users.append({"username": username, "errors": form.errors})
                        continue  # Skip to next user

                # Enroll the user in the batch
                StudentEnrollment.objects.create(student=user, batch=batch, course=batch.course, approval_status=True)

            except Exception as e:
                failed_users.append({"username": row.get("username", "Unknown"), "errors": str(e)})

        msg = (
            f"Users Created: {len(created_users)}, "
            f"Skipped (Already Exists): {len(skipped_users)}, "
            f"Failed: {len(failed_users)}"
        )
        success = True if created_users else False

    return redirect('home')
