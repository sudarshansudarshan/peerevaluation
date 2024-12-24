# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Course, Batch, Staffs, StudentEnrollment, Exam, Document, Statistics, Incentivization, TeachingAssistantAssociation
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course
from django.contrib.auth.models import User
from django.db import IntegrityError
import random
import csv
import json

def is_superuser(user):
    return user.is_superuser

# Overwrite User table from django to add method is_teacher
def is_teacher(self):
    return self.staffs.role == 'teacher'
User.add_to_class('is_teacher', is_teacher)


# Overwrite User table from django to add method is_student
def is_student(self):
    return not self.is_staff and not self.is_superuser
User.add_to_class('is_student', is_student)


# Overwrite User table from django to add method is_staff
def is_staff(self):
    return self.staffs.role == 'staff'
User.add_to_class('is_staff', is_staff)


def is_assistant(self):
    return self.staffs.role == 'assistant'
User.add_to_class('is_assistant', is_assistant)


@login_required(login_url="/login/")
def index(request):
    # Handle login for Admin
    if request.user.is_superuser:
        courses = Course.objects.all()
        batches = Batch.objects.all()
        teachers = User.objects.filter(is_superuser=False, is_staff=True, staffs__role='teacher')
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
            ta = User.objects.filter(is_staff=True, staffs__role='assistant').first()
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
        context = {'segment': 'index', 'courses': batches_list, 'is_ta': len(tas) > 0}
        html_template = loader.get_template('home/student/index.html')
        return HttpResponse(html_template.render(context, request))


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

            Staffs.objects.update_or_create(
                user=teacher,
                defaults={'role': 'teacher'}
            )

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
    

@user_passes_test(is_teacher)
# Generate UID for each student and Download the CSV file
def download_csv(request):
    if request.method == 'POST':
        try:
            # Get the selected batch
            batch_id = request.POST.get('batch')
            batch = Batch.objects.get(batch_id=batch_id)

            # Fetch students enrolled in the selected batch
            students = StudentEnrollment.objects.filter(batch=batch)

            # Prepare CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{batch.batch_id}_students.csv"'

            writer = csv.writer(response)
            writer.writerow(['Student Username', 'Peer Evaluation Number'])

            # Write student data if available, otherwise just the headers
            if students.exists():
                generated_numbers = set()  # Track unique peer evaluation numbers

                for enrollment in students:
                    student = enrollment.student
                    course = enrollment.course
                    random_number = random.randint(1000, 9999)

                    # Ensure unique random number
                    while random_number in generated_numbers:
                        random_number = random.randint(1000, 9999)
                    enrollment.uid = random_number
                    enrollment.save()

                    generated_numbers.add(random_number)
                    writer.writerow([student.username, random_number])

                    # Generate a unique UID for the student mapping
                    # unique_uid = f"{random.randint(100000, 999999)}-{batch.batch_id}"

                    # Append data to the student_mapping table
                    # student_mapping.objects.create_or_update(
                    #     student=student,
                    #     batch=batch,
                    #     uid=unique_uid
                    # )

            return response

        except Batch.DoesNotExist:
            messages.error(request, 'Batch not found.')
            return redirect('dashboard')  # Replace with the appropriate redirect
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('home')  # Replace with the appropriate redirect

    # If method is not POST, show the dashboard or an error
    messages.error(request, 'Invalid request method.')
    return redirect('home')  # Replace with the appropriate redirect


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
        print(batch, student_username)
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
                        batch=batch,
                        uid=f"{random.randint(10000, 99999)}"
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
        exams = Exam.objects.filter(batch__course__teacher=request.user)
        if request.user.is_teacher:
            exams = Exam.objects.filter(batch__teacher=request.user)
            return render(request, 'home/teacher/examination.html', {'exams': exams})


    if request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            batch_id = int(json.loads(data)['batch_id'])
            exam_id = json.loads(data)['exam_id']
            exam_name = json.loads(data)['exam_name']
            exam_date = json.loads(data)['exam_date']
            exam_duration = json.loads(data)['exam_duration']
            exam = Exam.objects.create(
                exam_id=exam_id,
                name=exam_name,
                date=exam_date,
                duration=exam_duration,
                batch_id=batch_id
            )
            messages.success(request, 'Exam added successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')
    

    elif request.method == 'DELETE':
        try:
            data = request.body.decode('utf-8')
            exam_id = json.loads(data)['exam_id']
            exam = Exam.objects.get(id=exam_id)
            exam.delete()
            messages.success(request, 'Exam deleted successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')