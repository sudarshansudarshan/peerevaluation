from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Course, Batch, StudentEnrollment, Exam, Statistics, Incentivization, TeachingAssistantAssociation, UIDMapping, Documents
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course
from django.contrib.auth.models import User
from django.db import IntegrityError
import random
import array
import csv
import json
from datetime import datetime, timedelta
from django.db.models import ExpressionWrapper, F, DateTimeField
from django.utils import timezone
import pytz
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode
from PIL import Image
import io
import tempfile

from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import user_passes_test
from fpdf import FPDF
import qrcode
import tempfile
from PyPDF2 import PdfMerger
import os
from io import BytesIO

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
                students_list.append({
                    'student_username': enrollment.student.username,
                    'student_email': enrollment.student.email,
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id
                })
            for ta in tas_for_batch:
                tas.append({
                    'ta_username': ta.teaching_assistant.username,
                    'ta_email': ta.teaching_assistant.email,
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id
                })

        # Pass data to the template
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
        batches = Batch.objects.all()
        tas = [{
            'batch': ta.batch.batch_id,
            'course': ta.batch.course.name,
            'ta_username': ta.teaching_assistant.username,
            'ta_email': ta.teaching_assistant.email,
        } for ta in TeachingAssistantAssociation.objects.filter(teaching_assistant=request.user)]
        batches_list = []
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
        # Define the India timezone
        india_timezone = pytz.timezone('Asia/Kolkata')

        # Get the current time in IST
        current_time = timezone.now().astimezone(india_timezone)
        exams = Exam.objects.filter(batch__in=batches)
        active_exams = []

        for exam in exams:
            if exam.date.tzinfo is None:
                exam_date = timezone.make_aware(exam.date, timezone=pytz.UTC)
            else:
                exam_date = exam.date
            exam_date = exam_date.astimezone(india_timezone) - timedelta(hours=5, minutes=30)
            expiration_time = exam_date + timedelta(minutes=exam.duration)
            if exam_date <= current_time <= expiration_time:
                active_exams.append(exam)
        context = {'segment': 'index', 'courses': batches_list, 'is_ta': len(tas) > 0, 'exams': active_exams}
        html_template = loader.get_template('home/student/index.html')
        return HttpResponse(html_template.render(context, request))


def generate_string():

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

    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS

    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)

    temp_pass = rand_digit + rand_upper + rand_lower
    for x in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)
    password = ""
    for x in temp_pass_list:
            password = password + x

    return (password)


@login_required
def enroll_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        try:
            course = Course.objects.get(course_id=course_id)
            batch = Batch.objects.filter(course=course).first()  # Assuming a batch exists for the course
            if batch:
                StudentEnrollment.objects.get_or_create(
                    student=request.user,
                    course=course,
                    batch=batch,
                    defaults=random.randint(10000, 99999)
                )
                messages.success(request, f"Successfully enrolled in {course.name}")
            else:
                messages.error(request, "No batch available for this course")
        except Course.DoesNotExist:
            messages.error(request, "Course not found")
    return redirect('student_enrollment')


# Invalid URL
@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
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
            # Create and save the course
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



def generate_student_pdf(student, exam, n_extra_pages):
    """Helper function to generate PDF for a single student"""
    pdf_files = []
    temp_files = []
    
    try:
        # Create QR Code
        qr = qrcode.QRCode(version=1, box_size=7, border=4)
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
            pdf.image(tmpfile.name, x=20, y=40, w=50, h=50)
            
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
                pdf.image(tmpfile.name, x=10, y=12, w=40, h=40)
            
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
            messages.error(request, f'Error generating PDFs: {str(e)}')
            return redirect('home')
    
    messages.error(request, 'Invalid request method.')
    return redirect('home')


# Enrollment of student
@login_required
def enrollment(request):

    if request.method == 'POST':     
        try:   
            data = request.body.decode('utf-8')
            batch_id = int(json.loads(data)['batch_id'])
            role = json.loads(data)['role']
            if role == "TA":
                username = str(json.loads(data)['student_username'])
                action = json.loads(data)['student_action']
                print(role, username, action)
                username = User.objects.get(email=username)
                print(username, action)
                studentenrollment = StudentEnrollment.objects.filter(batch_id=batch_id, student__username=username).first()
                print(studentenrollment)
                if studentenrollment:
                    if action == "1":
                        studentenrollment.approval_status = True
                        studentenrollment.save()
                        messages.success(request, 'Student approved successfully!')
                        print("Approved")
                    elif action == "0":
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
                    messages.success(request, 'Student enrolled successfully!')
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
        batches = Batch.objects.filter(teacher=request.user)
        tas = [{
            'batch': ta.batch,
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
        return render(request, 'home/student/ta_hub.html', {'batches': batches, 'ta': tas, 'is_ta': len(tas) > 0})

    # Associate Teaching associate with batch
    if request.method == 'POST':
        batch_id = request.POST.get('batch_id')
        ta_username = request.POST.get('teachingAssistantName')
        batch = Batch.objects.get(id=batch_id)
        ta = User.objects.get(username=ta_username)
        try:
            TeachingAssistantAssociation.objects.create(
                batch=batch,
                teaching_assistant=ta
            )
            messages.success(request, 'TA assigned successfully!')
        except IntegrityError:
            messages.error(request, 'TA already assigned to this batch.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect('home')


@login_required
def examination(request):

    if request.method == 'GET':
        if request.user.is_staff:
            batches = Batch.objects.filter(teacher=request.user)
            batch_data = []
            exams_list = []
            for batch in batches:
                exams = Exam.objects.filter(batch=batch, completed=False).first()
                if exams: exams_list.append(exams)
                batch_data.append({'batch': batch, 'exams': exams})

            return render(request, 'home/teacher/examination.html', {'batch_data': batch_data, 'exams': exams_list})


    elif request.method == 'POST':
        try:
            data = request.POST
            batch_id = int(data['batch_id'])
            exam_date = datetime.fromisoformat(data["exam_date"])
            exam_duration = int(data['duration'])
            num_que = int(data["num_que"])
            max_marks = int(data["max_marks"])
            k = int(data['k'])
            new_exam = Exam.objects.update_or_create(batch_id=batch_id,
                                                        defaults={
                                                            'date': exam_date,
                                                            'duration': exam_duration,
                                                            'number_of_questions': num_que,
                                                            'max_scores': max_marks,
                                                            'k': k,
                                                            'completed': False,
                                                        })
            if new_exam[1]:
                print("Updated exam")
                messages.success(request, 'Exam updated successfully!')
            else:
                print("Created exam")
                messages.success(request, 'Exam created successfully!')
            students_in_batch = StudentEnrollment.objects.filter(batch_id=batch_id)
            for student in students_in_batch:
                UIDMapping.objects.update_or_create(user=student.student,
                                                    exam=new_exam[0],
                                                    defaults={'uid': generate_string()})
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
                    messages.success(request, 'Exam deleted successfully!')
                except json.JSONDecodeError:
                    messages.error(request, 'Invalid JSON data.')
                except Exam.DoesNotExist:
                    messages.error(request, 'Exam not found.')
                except Exception as e:
                    messages.error(request, f'An error occurred: {str(e)}')
            else:
                messages.error(request, 'No data provided.')
            return redirect('examination')
    else:
        messages.error(request, 'Invalid request method.')
        return 


@login_required
def peer_evaluation(request):
    return render(request, 'home/student/peer_evaluation.html')


@login_required
def upload_evaluation(request):
    if request.method == "POST":
        uploaded_files = request.FILES.getlist("evaluationfile")  # Allow multiple files
        exam_id = request.POST.get("exam_id")

        if not uploaded_files:
            return redirect('home')

        try:
            # Fetch the exam object
            try:
                exam = Exam.objects.get(id=exam_id)
            except Exam.DoesNotExist:
                return redirect('home')

            # Limit students to one file
            if request.user.is_student():
                if len(uploaded_files) > 1:
                    return redirect('home')  # Students cannot upload multiple files
                
                uploaded_file = uploaded_files[0]  # Get the single file
                if uploaded_file.content_type != "application/pdf":
                    return redirect('home')

                # Process the single file for students
                pdf_content = uploaded_file.read()
                qr_content = convert_pdf_to_image_and_decode_qr(pdf_content)
                if not qr_content:
                    return redirect('home')
                final_filename = f"{qr_content}.pdf"

                uid_mapping = UIDMapping.objects.filter(user=request.user, exam=exam, uid=qr_content).first()
                if not uid_mapping:
                    return redirect('home')

                document = Documents.objects.filter(uid=qr_content).first()
                if not document:
                    Documents.objects.create(
                        uid=qr_content,
                        exam=exam,
                        document=final_filename,
                        uploaded_by=request.user
                    )
                    document.save()
                    with open(f"documents/{final_filename}", "wb") as f:
                        f.write(pdf_content)
                return redirect('home')

            elif request.user.is_teacher():
                for uploaded_file in uploaded_files:
                    if uploaded_file.content_type != "application/pdf":
                        continue  # Skip invalid files
                    
                    # Process each file
                    pdf_content = uploaded_file.read()
                    qr_content = convert_pdf_to_image_and_decode_qr(pdf_content)
                    if not qr_content:
                        continue  # Skip files without QR content
                    
                    final_filename = f"{qr_content}.pdf"

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
                    with open(f"documents/{final_filename}", "wb") as f:
                        f.write(pdf_content)
                return redirect('examination')

        except Exception as e:
            return render(request, "home/student/peer_evaluation.html",
                          {"error": f"An error occurred while processing the files: {str(e)}"})

    return render(request, "home/student/peer_evaluation.html")
