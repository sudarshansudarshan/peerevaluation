from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.db.models import Avg, Count, Q
from app.ocr import process_uploaded_pdf
import os
from random import shuffle, choice, sample
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

base_url = "http://127.0.0.1:8000/"

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
    Assign peer evaluations to students using a mapping approach.
    """
    num_peers = numberOfQuestions.objects.all().first().k  # Number of peers per document
    students = list(Student.objects.all())
    documents = list(document_instances)
    num_students = len(students)
    num_documents = len(documents)

    # Map student's own document
    student_documents = {document.uid.uid: document.id for document in documents}

    # Track assignments
    document_evaluations = defaultdict(list)  # document_id -> list of evaluator_ids
    student_evaluations = defaultdict(int)    # evaluator_id -> count of assigned documents

    # Rotate through students to assign evaluators for each document
    student_ids = [student.uid for student in students]

    for document in documents:
        document_id = document.id
        document_owner = document.uid.uid

        # Start assigning evaluators
        assigned_count = 0
        start_index = student_ids.index(document_owner) + 1  # Skip the owner
        current_index = start_index

        while assigned_count < num_peers:
            evaluator_id = student_ids[current_index % num_students]
            if (
                evaluator_id != document_owner
                and evaluator_id not in document_evaluations[document_id]
                and student_evaluations[evaluator_id] < num_peers
            ):
                # Assign evaluator to the document
                document_evaluations[document_id].append(evaluator_id)
                student_evaluations[evaluator_id] += 1
                assigned_count += 1

            # Move to the next student in a circular manner
            current_index += 1

    # Create PeerEvaluation objects and send emails
    for document_id, evaluator_ids in document_evaluations.items():
        for evaluator_id in evaluator_ids:
            PeerEvaluation.objects.create(
                evaluator_id=evaluator_id,
                evaluation_date=None,  # Placeholder
                evaluation=[],  # Placeholder
                feedback=[],  # Placeholder
                score=0,  # Placeholder
                document_id=document_id,
            )

            # Get evaluator's email
            student = Student.objects.get(uid=evaluator_id)
            email = student.student_id.email
            evaluation_link = f"{base_url}studentEval/{document_id}/{evaluator_id}/"
            try:
                send_peer_evaluation_email(evaluation_link, email)
            except:
                pass


# NOTE: The Admin dashboard
def AdminDashboard(request):
    """
    Handles the Admin Dashboard functionality, including document uploads and peer evaluation assignment.
    """
    # Check if the user in request
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return redirect('/login/')
    
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'Admin':
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
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return redirect('/login/')
    
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'TA':
        messages.error(request, 'Permission denied')
        return redirect('/login/')

    if request.method == 'POST':
        # Handle document upload logic
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
                error_message = f"Error in Peer Evaluation assignment: {str(e)}"
                print(error_message)  # Replace with a logging system if available

        # Start the thread for setPeerEval
        if document_instances:
            thread = threading.Thread(target=run_peer_eval, args=(document_instances,))
            thread.start()

        messages.success(request, 'Documents uploaded successfully! Peer evaluations are being assigned in the background.')
        return redirect('/TAHome/')

    # Analytics for Teacher Dashboard
    total_marks = numberOfQuestions.objects.all().first()
    if not total_marks:
        total_marks = 0
    else:
        total_marks = total_marks.total_marks

    # Analytics for Teacher Dashboard
    try:
        # Distribution of marks for students: Group by document_id and calculate average score
        marks_distribution = (
            PeerEvaluation.objects.values('document_id')
            .annotate(avg_score=Avg('score'))
            .order_by('-avg_score')[:10]  # Get top 10 documents based on avg_score
        )

        # Fetch top 10 documents' scores as a list of dictionaries
        top_students_scores = [
            {"document_id": item["document_id"], "avg_score": float(item["avg_score"])}  # Convert to float
            for item in marks_distribution
        ]
        
        # Total peer evaluations and their status
        total_peer_evaluations = PeerEvaluation.objects.count()
        evaluated_peer_evaluations = PeerEvaluation.objects.filter(evaluated=True).count()
        pending_peer_evaluations = PeerEvaluation.objects.filter(evaluated=False).count()

        peer_evaluations = {
            'total': total_peer_evaluations,
            'evaluated': evaluated_peer_evaluations,
            'pending': pending_peer_evaluations
        }

        # Number of documents submitted
        total_documents = documents.objects.count()

        tickets_raised = PeerEvaluation.objects.filter(ticket=1)

        # Data for rendering
        analytics_data = {
            'top_students_scores': top_students_scores,  # Add top 10 students' scores
            'total_documents': total_documents,
            'total_peer_evaluations': peer_evaluations['total'],
            'evaluated_peer_evaluations': peer_evaluations['evaluated'],
            'pending_peer_evaluations': peer_evaluations['pending'],
            'tickets_raised': [
                {
                    'evaluator': Student.objects.filter(uid=ticket.evaluator_id).first().student_id.username,
                    'document': documents.objects.filter(id=ticket.document_id).first().file.url,
                    'evaluation': ",".join([str(i) for i in eval(ticket.evaluation)]),
                    'evaluation_sheet': f"{base_url}studentEval/{ticket.document_id}/{ticket.evaluator_id}/",
                    'ticket': ticket.ticket,
                    'id': ticket.id
                } for ticket in tickets_raised
            ]
        }

    except Exception as e:
        analytics_data = {
            'top_students_scores': [],  # Default empty list
            'total_documents': 0,
            'total_peer_evaluations': 0,
            'evaluated_peer_evaluations': 0,
            'pending_peer_evaluations': 0,
        }

    return render(request, 'TAHome.html', {
        'users': user_profile.serialize(),
        'analytics_data': analytics_data,
        'num_ques': total_marks,
    })


# NOTE: This is Teacher dashboard
def TeacherHome(request):
    """
    Handles the Teacher Dashboard functionality, including document uploads and analytics.
    """
    # Check if the user is a Teacher
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return redirect('/login/')
    
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'Teacher':
        messages.error(request, 'Permission denied')
        return redirect('/login/')
    

    if request.method == 'POST':
        # Handle document upload logic
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
                error_message = f"Error in Peer Evaluation assignment: {str(e)}"
                print(error_message)  # Replace with a logging system if available

        # Start the thread for setPeerEval
        if document_instances:
            thread = threading.Thread(target=run_peer_eval, args=(document_instances,))
            thread.start()

        messages.success(request, 'Documents uploaded successfully! Peer evaluations are being assigned in the background.')
        return redirect('/TeacherHome/')

    # Analytics for Teacher Dashboard
    total_marks = numberOfQuestions.objects.all().first()
    if not total_marks:
        total_marks = 0
    else:
        total_marks = total_marks.total_marks

    try:
        # Distribution of marks for students: Group by document_id and calculate average score
        marks_distribution = (
            PeerEvaluation.objects.values('document_id')
            .annotate(avg_score=Avg('score'))
            .order_by('-avg_score')[:10]  # Get top 10 documents based on avg_score
        )

        # Fetch top 10 documents' scores as a list of dictionaries
        top_students_scores = [
            {"document_id": item["document_id"], "avg_score": float(item["avg_score"])}  # Convert to float
            for item in marks_distribution
        ]
        
        # Total peer evaluations and their status
        total_peer_evaluations = PeerEvaluation.objects.count()
        evaluated_peer_evaluations = PeerEvaluation.objects.filter(evaluated=True).count()
        pending_peer_evaluations = PeerEvaluation.objects.filter(evaluated=False).count()

        peer_evaluations = {
            'total': total_peer_evaluations,
            'evaluated': evaluated_peer_evaluations,
            'pending': pending_peer_evaluations
        }

        # Number of documents submitted
        total_documents = documents.objects.count()

        tickets_raised = PeerEvaluation.objects.filter(ticket=2)

        # Data for rendering
        analytics_data = {
            'top_students_scores': top_students_scores,  # Add top 10 students' scores
            'total_documents': total_documents,
            'total_peer_evaluations': peer_evaluations['total'],
            'evaluated_peer_evaluations': peer_evaluations['evaluated'],
            'pending_peer_evaluations': peer_evaluations['pending'],
            'tickets_raised': [
                {
                    'evaluator': Student.objects.filter(uid=ticket.evaluator_id).first().student_id.username,
                    'document': documents.objects.filter(id=ticket.document_id).first().file.url,
                    'evaluation': ".".join([str(i) for i in eval(ticket.evaluation)]),
                    'evaluation_sheet': f"{base_url}studentEval/{ticket.document_id}/{ticket.evaluator_id}/",
                } for ticket in tickets_raised
            ]
        }
    except Exception as e:
        analytics_data = {
            'top_students_scores': [],  # Default empty list
            'total_documents': 0,
            'total_peer_evaluations': 0,
            'evaluated_peer_evaluations': 0,
            'pending_peer_evaluations': 0,
        }

    return render(request, 'TeacherHome.html', {
        'users': user_profile.serialize(),
        'analytics_data': analytics_data,
        'num_ques': total_marks,
    })


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
                            'username': data[1],
                            'first_name': data[0].split()[0],
                            'last_name': data[0].split()[1] if len(data[0].split()) > 1 else '',
                        }
                    )
                    if created:
                        user.set_password(generate_password(10))
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
            if user_profile.password_updated:
                return redirect(f"/{user_profile.role}Home/")
            else:
                messages.error(request, "Please change your password to continue.")
                return redirect('/changePassword/')
    
    # Render the login page template (GET request)
    return render(request, 'login.html')


# Regex for validating a strong password
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


def register_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the provided username already exists
        user = User.objects.filter(username=email)
        
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
            username=email,
            email=email
        )
        user.set_password(password)
        user.save()

        user_id = User.objects.get(username=email).id
        user_profile = UserProfile(user_id=user_id, role="Student", password_updated=True)
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
                            'username': data[1],
                            'first_name': data[0].split()[0],
                            'last_name': data[0].split()[1] if len(data[0].split()) > 1 else ''
                        }
                    )

                    if created:

                        random_password = generate_password(10)
                        html_message = render_to_string(
                            "ForgotPasswordMailTemplate.html",  # Path to your email template
                            {
                                "username": data[1],
                                "new_password": random_password  # Link to the evaluation
                            },
                        )
                        plain_message = strip_tags(html_message)  # Fallback plain text version

                        # Send the email
                        send_mail(
                            subject="Account created : Credentials",
                            message=plain_message,
                            from_email="no-reply@evaluation-system.com",
                            recipient_list=[data[1]],
                            html_message=html_message,  # Attach the HTML message
                            fail_silently=False,
                        )
                        user.set_password(random_password)
                        user.save()

                        user_id = User.objects.get(username=data[1]).id
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
        number, total_marks, k = request.POST.get('num-questions'), request.POST.get('total_marks'), request.POST.get('k')
        numQue = numberOfQuestions.objects.all().first()
        if not numQue:
            numQue = numberOfQuestions(number=number, total_marks=total_marks, k=k)
        else:
            numQue.number = number
            numQue.total_marks = total_marks
            numQue.k = k
        numQue.save()
        messages.success(request, f'Number of questions: {number} | Total Marks: {total_marks} | Number of evaluations: {k} updated successfully.')
        messages.info(request, 'Please upload documents to assign peer evaluations.')
        return redirect(f"/{current_user_profile.role}Home/")
    return redirect('/logout/')


# NOTE: Change password route
def changePassword(request):
    current_user_profile = UserProfile.objects.filter(user=request.user).first()
    if not current_user_profile:
        messages.error(request, 'You do not have permission to access thiis page.')
        return redirect(f"/{current_user_profile.role}Home/")

    if request.method == 'POST':
        # Retrieve the password and confirmation from the POST data
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        # Define the password pattern for validation
        # At least 8 characters, one letter, one number, and one special character (@, #, $, %, *)
        password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@#$%*])[A-Za-z\d@#$%*]{8,}$')

        # Validate password strength
        if not password:
            messages.error(request, "Password field cannot be empty.")
            return redirect('/changePassword/')
        
        elif not password_pattern.match(password):
            messages.error(request, "Password must be at least 8 characters long, include at least one letter, one number, and one special character (@, #, $, %, *).")
            return redirect('/changePassword/')  # Update with your actual URL

        # Validate password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/changePassword/')  # Update with your actual URL

        # If all validations pass, update the password
        try:
            user = User.objects.get(id=current_user_profile.user_id)
            user.set_password(password)
            user.save()
            current_user_profile.password_updated = True
            current_user_profile.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('/logout/')  # Redirect to logout or another appropriate page
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('/logout/')  # Update with your actual URL

    return render(request, 'NewPassword.html')


def studentHome(request):
    try:
        # Step 1: Get UID of the current user from the Student table
        student_profile = Student.objects.filter(student_id=request.user).first()
        
        if not student_profile:
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
                        'id': review.id,
                        'evaluator_id': review.evaluator_id,
                        'evaluation': review.evaluation or [],
                        'feedback': "No feedback found" if " ".join(eval(review.feedback)).strip() == "" else ",".join(eval(review.feedback)).strip(),
                        'ticket': review.ticket,
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

        own_pdf = documents.objects.filter(uid=student_profile).first()

        # Render the data in the studentHome template
        return render(request, 'StudentHome.html', {
            'evaluation_files': evaluation_files_data,
            'own_documents': own_documents_data,
            'own_pdf': own_pdf.file.url
        })

    except Exception as e:
        # Handle unexpected errors
        print(f"Error fetching data: {e}")
        return render(request, 'StudentHome.html', {
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
    total_marks = numberOfQuestions.objects.all().first().total_marks

    # Check user authentication and access permissions
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not request.user.is_authenticated or not user_profile or not document or not evaluation:
        messages.error(request, 'Permission denied.')
        return redirect('/logout/')
    
    if user_profile.role != 'Student':
        pass
    elif evaluation.evaluated:
        messages.error(request, 'This document has already been evaluated.')
        return redirect(f'/{user_profile.role}Home/')

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
        'total_marks': round(total_marks/num_questions)
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
        evaluation.ticket = 0
        evaluation.save()

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect(f'/{user_profile.role}Home/')  # Redirect to a relevant page after submission

    # Render the template for viewing the document and providing evaluation
    return render(request, 'AssignmentView.html', context)


def forgetPassword(request):
    if request.method == 'POST':
        # Fetch the user object based on the provided email
        user = User.objects.filter(username=request.POST.get('username')).first()
        user_profile = UserProfile.objects.filter(user_id=user.id).first()

        if user:
            random_password = generate_password(10)
            html_message = render_to_string(
                "ForgotPasswordMailTemplate.html",  # Path to your email template
                {
                    "username": user.username,
                    "new_password": random_password  # Link to the evaluation
                },
            )
            plain_message = strip_tags(html_message)  # Fallback plain text version

            # Send the email
            send_mail(
                subject="Peer Evaluation Forget Password credentials",
                message=plain_message,
                from_email="no-reply@evaluation-system.com",
                recipient_list=[user.email],
                html_message=html_message,  # Attach the HTML message
                fail_silently=False,
            )
            user.set_password(random_password)
            user.save()
            user_profile.password_updated = False
            user_profile.save()
            messages.success(request, 'Password reset email sent successfully!')
        else:
            messages.error(request, 'User not found.')
        return redirect('/login/')
    return render(request, 'changePassword.html')



def raise_ticket(request, doc_id):
    current_user_profile = UserProfile.objects.filter(user=request.user).first()
    if not current_user_profile or current_user_profile.role not in ['TA', 'Student']:
        messages.error(request, 'You do not have permission to modify roles.')
        return redirect(f"/{current_user_profile.role}Home/")
    
    if request.method == 'POST':
        if current_user_profile.role == 'TA':
            peerevaluation = PeerEvaluation.objects.filter(id=doc_id).first()
            peerevaluation.ticket = 2
        elif current_user_profile.role == 'Student':
            peerevaluation = PeerEvaluation.objects.filter(id=doc_id).first()
            peerevaluation.ticket = 1
        peerevaluation.save()
        messages.success(request, 'Ticket raised successfully!')
        return redirect(f"/{current_user_profile.role}Home/")


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

