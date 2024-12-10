from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from app.ocr import process_uploaded_pdf
import os
from random import shuffle
from collections import defaultdict
import random
from math import sqrt, ceil, floor
from collections import defaultdict
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
# import google.generativeai as genai
import json
import base64
import threading
from django.contrib import messages
import re
import random
import array

base_url = "http://127.0.0.1:8080/"

# Regex for validating a strong password
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


def generate_password(length):
    MAX_LEN = 12

    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']

    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']

    SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>', 
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


# NOTE: Send email to the assigned peer
def send_peer_evaluation_email(evaluation_link, email_id):
    """
    Sends a peer evaluation email to the assigned peer with an HTML template.
    """
    subject = "Peer Evaluation Request"
    
    # Render the HTML template
    html_message = render_to_string(
        "EvalMailTemplate.html",  # Path to your email template
        {
            "evaluation_link": evaluation_link,  # Link to the evaluation
        },
    )
    plain_message = strip_tags(html_message)  # Fallback plain text version
    
    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email="no-reply@evaluation-system.com",
        recipient_list=[email_id],
        html_message=html_message,  # Attach the HTML message
        fail_silently=False,)


def setPeerEval(document_instances):
    """
    Assign peer evaluations to students.
    """
    # Calculate the number of peers required per document
    num_peers = floor(sqrt(len(document_instances)))
    all_students = list(Student.objects.all())
    shuffle(all_students)

    # Initialize a distribution map for each student
    student_distribution = {student.uid: num_peers for student in all_students}

    # Shuffle document instances to distribute evaluations randomly
    peer_evaluations_assigned = defaultdict(int)

    for document in document_instances:
        # Track how many students have been assigned to this document
        current_assigned_count = 0

        for student in all_students:
            if (
                student.uid != document.uid.uid  # Avoid assigning a student to their own document
                and student_distribution[student.uid] > 0  # Student can evaluate more
                and peer_evaluations_assigned[document.id] < num_peers  # Document needs more reviewers
            ):
                # Assign the evaluation
                PeerEvaluation.objects.create(
                    evaluator_id=student.uid,
                    evaluation_date=None,  # Placeholder
                    evaluation=[],  # Placeholder
                    feedback=[],  # Placeholder
                    score=0,  # Placeholder
                    document=document,
                )
                email = User.objects.get(pk=student.student_id_id).email
                student_distribution[student.uid] -= 1
                peer_evaluations_assigned[document.id] += 1
                current_assigned_count += 1
                # encoded_doc_id = encode_id(str(document.id) + " " + str(student.uid))
                evaluation_link = f"{base_url}studentEval/{document.id}/{student.uid}/"
                send_peer_evaluation_email(evaluation_link, email)
                
                if current_assigned_count == num_peers:
                    break

    return  # Function ends here with evaluations assigned


# NOTE: The Admin dashboard
def AdminDashboard(request):
    """
    Handles the Admin Dashboard functionality, including document uploads and peer evaluation assignment.
    """
    # Check if the user is an admin
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'Admin' or not request.user.is_authenticated:
        messages.error(request, 'Permission denied')
        return redirect('/login/')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        user = User.objects.get(username=request.user)
        docs = request.FILES.getlist('doc')  # Get multiple uploaded files
        document_instances = []

        for doc in docs:
            # Process each uploaded PDF and retrieve UID
            uid, processed_doc = process_uploaded_pdf(doc)

            # Ensure the student exists
            student = Student.objects.filter(uid=uid).first()
            if not student:
                continue

            # Create and save the document object
            document = documents(
                title=title,
                description=description,
                user_id=user,
                uid=student,
                file=processed_doc
            )
            document.save()
            document_instances.append(document)

        # Background thread function for calling setPeerEval
        def run_peer_eval(documents):
            try:
                setPeerEval(documents)
            except Exception as e:
                # Log the error and notify the admin (adjust logging as per your project setup)
                error_message = f"Error in Peer Evaluation assignment: {str(e)}"
                print(error_message)  # Replace with a logging system if available

        # Start the thread for setPeerEval
        if document_instances:
            thread = threading.Thread(target=run_peer_eval, args=(document_instances,))
            thread.start()

        messages.success(request, 'Documents uploaded successfully! Peer evaluations are being assigned in the background.')
        return redirect('/AdminHome/')

    return render(request, 'AdminDashboard.html', {'users': user_profile.serialize()})


# NOTE: This is TA dashboard
def TAHome(request):
    """
    Handles the TA Dashboard functionality, including document uploads and peer evaluation assignment.
    """
    # Check if the user is an TA
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'TA' or not request.user.is_authenticated:
        messages.error(request, 'Permission denied')
        return redirect('/login/')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        user = User.objects.get(username=request.user)
        docs = request.FILES.getlist('doc')  # Get multiple uploaded files
        document_instances = []

        for doc in docs:
            # Process each uploaded PDF and retrieve UID
            uid, processed_doc = process_uploaded_pdf(doc)

            # Ensure the student exists
            student = Student.objects.filter(uid=uid).first()
            if not student:
                continue

            # Create and save the document object
            document = documents(
                title=title,
                description=description,
                user_id=user,
                uid=student,
                file=processed_doc
            )
            document.save()
            document_instances.append(document)

        # Call setPeerEval function only once with the collected document instances
        if document_instances:
            setPeerEval(document_instances)

        messages.success(request, 'Documents uploaded and Peer evaluations assigned successfully!')
        return redirect('/TAHome/')

    return render(request, 'TAHome.html', {'users': user_profile.serialize()})


# NOTE: This is Teacher dashboard
def TeacherHome(request):
    """
    Handles the Teacher Dashboard functionality, including document uploads and peer evaluation assignment.
    """
    # Check if the user is an Teacher
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'Teacher' or not request.user.is_authenticated:
        messages.error(request, 'Permission denied')
        return redirect('/login/')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        user = User.objects.get(username=request.user)
        docs = request.FILES.getlist('doc')  # Get multiple uploaded files
        document_instances = []

        for doc in docs:
            # Process each uploaded PDF and retrieve UID
            uid, processed_doc = process_uploaded_pdf(doc)

            # Ensure the student exists
            student = Student.objects.filter(uid=uid).first()
            if not student:
                continue

            # Create and save the document object
            document = documents(
                title=title,
                description=description,
                user_id=user,
                uid=student,
                file=processed_doc
            )
            document.save()
            document_instances.append(document)

        # Call setPeerEval function only once with the collected document instances
        if document_instances:
            setPeerEval(document_instances)

        messages.success(request, 'Documents uploaded and Peer evaluations assigned successfully!')
        return redirect('/TeacherHome/')

    return render(request, 'TeacherHome.html', {'users': user_profile.serialize()})


# NOTE: This is route for uploading bunch of PDF Files and creating the users
def uploadFile(request):
    user_profile = UserProfile.objects.filter(user=user).first()
    if request.method == 'POST':
        file = request.FILES.get('csv-upload')
        file_data = file.read().decode("utf-8")
        file_data = file_data.strip()
        lines = file_data.split("\n")

        # Remove the first row (header)
        lines.pop(0)

        # Delete all existing Student and document records
        documents.objects.all().delete()
        Student.objects.all().delete()

        for line in lines:
            if line:
                data = line.split(",")
                try:
                    # Get or create User instance
                    user, created = User.objects.get_or_create(
                        email=data[1],
                        defaults={
                            'username': data[1].split("@")[0],
                            'first_name': data[0].split()[0],
                            'last_name': data[0].split()[1] if len(data[0].split()) > 1 else '',
                        }
                    )
                    if created:
                        user.set_password("Abcd@1234")
                        user.save()

                    # Create or update Student record
                    Student.objects.update_or_create(
                        student_id=User.objects.get(email=data[1]),
                        defaults={'uid': data[2]}
                    )
                except Exception as e:
                    print(f"Error processing line: {line} - {e}")
                    continue

        messages.info(request, 'Students uploaded successfully!')
        return redirect(f"/{user_profile.role}Home/")
    return redirect('/logout/')


# NOTE: This is route for logging in
def login_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            user_profile = UserProfile.objects.filter(user=user).first()
            login(request, user)
            return redirect(f"/{user_profile.role}Home/")
    
    # Render the login page template (GET request)
    return render(request, 'login.html')

# Regex for validating a strong password
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


def register_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(first_name, last_name, username, email, password)

        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)
        
        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect('/register/')

        # Validate the password strength using regex
        if not re.match(PASSWORD_REGEX, password):
            messages.error(
                request,
                "Password must be at least 8 characters long, include at least one letter, one number, and one special character."
            )
            return redirect('/register/')

        # Create a new User object with the provided information
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        
        # Set the user's password and save the user object
        user.set_password(password)
        user.save()

        user_id = User.objects.get(username=username).id
        user_profile = UserProfile(user_id=user_id, role="Student")
        user_profile.save()
        
        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return redirect('/login/')
    
    # Render the registration page template (GET request)
    return render(request, 'register.html')


def evaluationList(request):
    docs = []
    for doc in documents.objects.all():
        evaluations = PeerEvaluation.objects.filter(document_id=doc.id)
        docs.append({
            'doc': doc,
            'evaluations': evaluations
        })
    return render(request, 'docs.html', {'docs': docs})


# NOTE: This is route for uploading CSV file
def uploadCSV(request):
    # Check if the user has a role that allows file uploads (Admin only)
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role not in ["TA", "Admin", "Teacher"] or not request.user.is_authenticated:
        messages.error(request, 'Permission denied')
        return redirect('/logout/')

    if request.method == 'POST':
        file = request.FILES.get('csv-upload')
        file_data = file.read().decode("utf-8")
        file_data = file_data.strip()
        lines = file_data.split("\n")

        # Remove the first row (header)
        lines.pop(0)

        # Delete all physical files associated with documents
        documents_to_delete = documents.objects.all()
        for doc in documents_to_delete:
            if doc.file and os.path.isfile(doc.file.path):  # Check if file exists
                try:
                    os.remove(doc.file.path)  # Delete the file from the file system
                except Exception as e:
                    print(f"Error deleting file {doc.file.path}: {e}")

        # Delete all existing Student and document records
        documents.objects.all().delete()
        Student.objects.all().delete()
        PeerEvaluation.objects.all().delete()

        for line in lines:
            if line:
                data = line.split(",")
                try:
                    # Get or create User instance
                    user, created = User.objects.get_or_create(
                        email=data[1],
                        defaults={
                            'username': data[1].split("@")[0],
                            'first_name': data[0].split()[0],
                            'last_name': data[0].split()[1] if len(data[0].split()) > 1 else '',
                        }
                    )
                    if created:
                        user.set_password("Abcd@1234")
                        user.save()

                        user_id = User.objects.get(username=data[1].split("@")[0]).id
                        new_user_profile = UserProfile(user_id=user_id, role="Student")
                        new_user_profile.save()

                    # Create or update Student record
                    Student.objects.update_or_create(
                        student_id=User.objects.get(email=data[1]),
                        defaults={'uid': data[2]}
                    )
                except Exception as e:
                    print(f"Error processing line: {line} - {e}")
                    continue

        messages.info(request, 'Students uploaded successfully!')
        return redirect(f"/{user_profile.role}Home/")
    return redirect(f"/{user_profile.role}Home/")


# TODO: Working fine but getting status code 302
def change_role(request):

    if request.method == 'POST':
        current_user_profile = UserProfile.objects.filter(user=request.user).first()
        if not current_user_profile or current_user_profile.role not in ['TA', 'Teacher', 'Admin']:
            messages.error(request, 'You do not have permission to modify roles.')
            return redirect(f"/{current_user_profile.role}Home/")

        try:
            user = User.objects.get(username=request.POST.get('username'))
            user_profile = UserProfile.objects.filter(user_id=user.id).first()
            if not user_profile:
                user_profile = UserProfile(user_id=user.id, role=request.POST.get('role'))
                user_profile.save()
            else:
                user_profile.role = request.POST.get('role')
                user_profile.save()

            messages.success(request, f"Role for {user.username} updated.")
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect(f"/{current_user_profile.role}Home/")


# NOTE: Update number of questions in particular test
def questionNumbers(request):
    current_user_profile = UserProfile.objects.filter(user=request.user).first()
    if request.method == 'POST':
        number = request.POST.get('num-questions')
        numQue = numberOfQuestions.objects.filter(id=1).first()
        if not numQue:
            numQue = numberOfQuestions(number=number)
        else:
            numQue.number = number
        numQue.save()
        messages.success(request, 'Number of questions updated successfully!')
        return redirect(f"/{current_user_profile.role}Home/")
    return redirect('/logout/')


# NOTE: Change password route
def changePassword(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user.set_password(request.POST.get('password'))
        user.save()
        messages.error(request, 'Password changed')
        return redirect('/logout/')
    return render(request, 'login.html')


def forgetPassword(request):
    if request.method == 'POST':
        return redirect('/login/')
    return render(request, 'changePassword.html')


def studentHome(request):
    try:
        # Step 1: Get UID of the current user from the Student table
        student_profile = Student.objects.filter(student_id=request.user).first()
        if not student_profile:
            # Step 2: Redirect to logout if UID is not found
            messages.error(request, "Invalid student profile. Wait for admin approval.")
            return redirect('/logout/')

        uid = student_profile.uid  # UID of the current user

        # Step 3: Check for all UIDs in PeerEvaluation table for associated document IDs
        peer_evaluation_docs = PeerEvaluation.objects.filter(evaluator_id=uid).values('document_id', 'evaluated')

        # Map document IDs to their evaluated_column values
        peer_evaluation_map = {item['document_id']: item['evaluated'] for item in peer_evaluation_docs}

        # Step 4: Fetch all documents from the `documents` table
        evaluation_files = documents.objects.filter(id__in=peer_evaluation_map.keys()).select_related('uid')

        # Prepare data for the fetched documents
        evaluation_files_data = [
            {
                'document_title': doc.title,
                'description': doc.description,
                'file_url': f"/studentEval/{doc.id}/{uid}",
                'evaluated': peer_evaluation_map.get(doc.id)  # Get the evaluated_column value
            }
            for doc in evaluation_files
        ]

        # Fetch documents submitted by the student
        own_documents = documents.objects.filter(uid=student_profile).prefetch_related('peerevaluation_set')

        # Prepare data for the student's own documents
        own_documents_data = [
            {
                'document_title': doc.title,
                'description': doc.description,
                'peer_reviews': [
                    {
                        'evaluator_id': review.evaluator_id,
                        'evaluation': review.evaluation or [],
                        'feedback': "No feedback found" if " ".join(eval(review.feedback)).strip() == "" else ",".join(eval(review.feedback)).strip(),
                        'score': review.score or 0
                    }
                    for review in doc.peerevaluation_set.all()
                ],
                'aggregate_marks': (
                    sum(review.score or 0 for review in doc.peerevaluation_set.all()) / max(doc.peerevaluation_set.count(), 1)
                ),  # Calculate average marks
            }
            for doc in own_documents
        ]

        # Render the data in the studentHome template
        return render(request, 'studentHome.html', {
            'evaluation_files': evaluation_files_data,
            'own_documents': own_documents_data,
        })

    except Exception as e:
        # Handle unexpected errors
        print(f"An error occurred while loading the student home page: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return render(request, 'studentHome.html', {
            'evaluation_files': [],
            'own_documents': [],
        })


def deleteDocs(request):
    current_user_profile = UserProfile.objects.filter(user=request.user).first()
    if not current_user_profile or current_user_profile.role not in ['TA', 'Teacher', 'Admin']:
        messages.error(request, 'You do not have permission to modify roles.')
        return redirect(f"/{current_user_profile.role}Home/")
    # Delete all physical files associated with documents
    documents_to_delete = documents.objects.all()
    for doc in documents_to_delete:
        if doc.file and os.path.isfile(doc.file.path):  # Check if file exists
            try:
                os.remove(doc.file.path)  # Delete the file from the file system
            except Exception as e:
                print(f"Error deleting file {doc.file.path}: {e}")
                messages.error(request, f"Error deleting file {doc.file.path}.")
    # Delete all existing Student and document records
    documents.objects.all().delete()
    Student.objects.all().delete()
    PeerEvaluation.objects.all().delete()
    messages.success(request, 'All documents deleted successfully!')
    return redirect(f"/{current_user_profile.role}Home/")


# NOTE: view and evaluate the assignment
def studentEval(request, doc_id, eval_id):
    # Parse document and evaluator IDs
    try:
        document_id, evaluator_id = int(doc_id), int(eval_id)
    except ValueError:
        messages.error(request, 'Invalid document or evaluator ID.')
        return redirect('/logout/')

    # Fetch document and evaluation objects
    document = documents.objects.filter(id=document_id).first()
    evaluation = PeerEvaluation.objects.filter(document_id=document_id, evaluator_id=evaluator_id).first()

    # Check user authentication and access permissions
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not request.user.is_authenticated or not user_profile or not document or not evaluation:
        messages.error(request, 'Permission denied.')
        return redirect('/logout/')
    if evaluation.evaluated:
        messages.error(request, 'This document has already been evaluated.')
        return redirect('/StudentHome/')

    # Fetch the number of questions
    number_of_questions = numberOfQuestions.objects.filter(id=1).first()
    if not number_of_questions:
        messages.error(request, 'Configuration error: Number of questions not set.')
        return redirect('/logout/')
    num_questions = number_of_questions.number

    # Prepare data for rendering the template
    context = {
        'document_url': document.file.url,  # Assuming the 'file' field stores the document file
        'document_title': document.title,
        'document_description': document.description,
        'number_of_questions': [i + 1 for i in range(num_questions)],
    }

    # Handle POST request for submitting the evaluation
    if request.method == 'POST':
        evaluations = []
        feedback = []

        for i in range(1, num_questions + 1):
            # Fetch evaluation and feedback for each question
            evaluations.append(int(request.POST.get(f'question-{i}', 0)))
            feedback.append(request.POST.get(f'feedback-{i}', '').strip())

        # Calculate total marks
        total_marks = sum(evaluations)

        # Update the evaluation record
        evaluation.evaluation = evaluations
        evaluation.feedback = feedback
        evaluation.score = total_marks
        evaluation.evaluated = True
        evaluation.save()

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('/StudentHome/')  # Redirect to a relevant page after submission

    # Render the template for viewing the document and providing evaluation
    return render(request, 'AssignmentView.html', context)


def forgot_password(request):
    if request.method == 'POST':
        # Fetch the user object based on the provided email
        user = User.objects.filter(email=request.POST.get('email')).first()
        if user:
            token = base64.b64encode(os.urandom(24)).decode('utf-8')
            # Send email


# # NOTE: Send email to the assigned peer
# def send_peer_evaluation_email(evaluation_link, email_id):
#     """
#     Sends a peer evaluation email to the assigned peer with an HTML template.
#     """
#     subject = "Peer Evaluation Request"
    
#     # Render the HTML template
#     html_message = render_to_string(
#         "EvalMailTemplate.html",  # Path to your email template
#         {
#             "evaluation_link": evaluation_link,  # Link to the evaluation
#         },
#     )
#     plain_message = strip_tags(html_message)  # Fallback plain text version
    
#     # Send the email
#     send_mail(
#         subject=subject,
#         message=plain_message,
#         from_email="no-reply@evaluation-system.com",
#         recipient_list=[email_id],
#         html_message=html_message,  # Attach the HTML message
#         fail_silently=False,
#     )


def send_reminder_mail(request):
    current_user_profile = UserProfile.objects.filter(user=request.user).first()
    if not current_user_profile or current_user_profile.role not in ['TA', 'Teacher', 'Admin']:
        messages.error(request, 'You do not have permission to modify roles.')
        return redirect(f"/{current_user_profile.role}Home/")
    
    # Fetch PeerEvaluation entries where 'evaluated' is False
    pending_evaluations = PeerEvaluation.objects.filter(evaluated=False)

    # Create a set to store email IDs to avoid duplicates
    email_ids = set()

    for evaluation in pending_evaluations:
        try:
            # Fetching the evaluator's student profile
            student = Student.objects.filter(uid=evaluation.evaluator_id).select_related('student_id').first()
            
            if student and student.student_id.email:
                email_ids.add(student.student_id.email)  # Add email to the set
        except Exception as e:
            print(f"Error fetching student email for evaluator_id {evaluation.evaluator_id}: {e}")
            continue

    # Send reminder emails to all collected email IDs
    if email_ids:
        for email in email_ids:
            try:
                send_mail(
                    subject="Reminder: Pending Evaluation",
                    message="Dear Student,\n\nYou have pending evaluations. Please complete them as soon as possible.\n\nThank you!",
                    from_email="admin@example.com",  # Update with your email
                    recipient_list=[email],
                )
            except Exception as e:
                messages.error(request, f"Error sending email to {email}: {e}")
    
    # Display a success message on the frontend
    messages.success(request, "Reminder emails sent successfully!")    
    return redirect(f"/{current_user_profile.role}Home/")


def home(request):
    return redirect('/login/')

def logout_user(request):
    logout(request)
    return redirect('/login/')