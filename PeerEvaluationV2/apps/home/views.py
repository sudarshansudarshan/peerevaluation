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
from .models import Course, Batch, Staffs, StudentEnrollment, Exam, Document, Statistics, Incentivization
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course
from django.contrib.auth.models import User
from django.db import IntegrityError
import random
import csv
import json

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


@login_required(login_url="/login/")
def index(request):
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
    elif request.user.is_staff:
        # Check the user_id of current user
        user_id = request.user.id
        staff = Staffs.objects.get(user_id=user_id)
        # Teacher
        if staff.role == 'teacher':
            batches = Batch.objects.filter(teacher=request.user)
            batches_list = []
            for batch in batches:
                batches_list.append({
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id,
                    'teacher': batch.teacher.username,
                    'strength': StudentEnrollment.objects.filter(batch=batch, approval_status=True).count()
                })
            
            # Fetch students for these batches
            students_list = []
            for batch in batches:
                students = StudentEnrollment.objects.filter(batch=batch, approval_status=True)
                for enrollment in students:
                    students_list.append({
                        'student_username': enrollment.student.username,
                        'student_email': enrollment.student.email,
                        'batch_id': batch.batch_id,
                        'course_name': batch.course.name,
                        'course_id': batch.course.course_id
                    })

            # Pass data to the template
            context = {
                'segment': 'index',
                'batches': batches_list,
                'students': students_list
            }
        
        if staff.role == 'assistant':
            batches = Batch.objects.filter(teacher=request.user)
            batches_list = []
            for batch in batches:
                batches_list.append({
                    'batch_id': batch.batch_id,
                    'course_name': batch.course.name,
                    'course_id': batch.course.course_id,
                    'teacher': batch.teacher.username,
                    'strength': StudentEnrollment.objects.filter(batch=batch, approval_status=True).count()
                })
            
            # Fetch students for these batches
            students_list = []
            for batch in batches:
                students = StudentEnrollment.objects.filter(batch=batch, approval_status=True)
                for enrollment in students:
                    students_list.append({
                        'student_username': enrollment.student.username,
                        'student_email': enrollment.student.email,
                        'batch_id': batch.batch_id,
                        'course_name': batch.course.name,
                        'course_id': batch.course.course_id
                    })

            # Pass data to the template
            context = {
                'segment': 'index',
                'batches': batches_list,
                'students': students_list
            }
            html_template = loader.get_template('home/teacher/index.html')
            return HttpResponse(html_template.render(context, request))
        
        html_template = loader.get_template('home/teacher/index.html')
        return HttpResponse(html_template.render(context, request))
    
    elif not request.user.is_staff or not request.user.is_superuser: # Student role
        enrolled_courses = StudentEnrollment.objects.filter(student=request.user).values_list('batch', flat=True)
        print(enrolled_courses)
        batches = Batch.objects.all()
        batches_list = []
        for batch in batches:
            print(batch.id)
            course = batch.course
            batches_list.append({
                'course_id': course.course_id,
                'batch': batch.batch_id,
                'name': course.name,
                'description': course.description,
                'is_public': course.is_public,
                'start_date': course.start_date,
                'end_date': course.end_date,
                'is_enrolled': batch.id in enrolled_courses
            })
        context = {'segment': 'index', 'courses': batches_list, 'data': 'data'}
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


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def course(request):

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


def enrollment(request):
    if request.method == 'POST':
        course_id, batch_id = str(request.POST.get('details')).split("_")
        course = Course.objects.get(course_id=course_id)
        batch = Batch.objects.get(batch_id=batch_id)
        student_username = request.user.username

        if course and student_username:
            try:
                student = User.objects.get(username=student_username)

                enrolment = StudentEnrollment.objects.filter(student_id=student.id, batch_id=batch.id).first()
                print(enrolment)

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
                        course=course,
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


@login_required(login_url="/login/")
def delete_course(request):
    """
    Handles the deletion of a course via POST request.
    """
    if request.method == 'POST':
        # Retrieve the course_id from the POST data
        course_id = request.POST.get('course_id')

        # Ensure the course exists
        course = get_object_or_404(Course, course_id=course_id)

        # Check and clean up related records
        related_batches = Batch.objects.filter(course=course).count()
        related_enrollments = StudentEnrollment.objects.filter(course=course).count()

        if related_batches > 0 or related_enrollments > 0:
            messages.warning(request, f"Deleting '{course.name}' will also delete {related_batches} batches and {related_enrollments} enrollments.")

        # Clean up related models explicitly (optional if CASCADE is used)
        Batch.objects.filter(course=course).delete()
        StudentEnrollment.objects.filter(course=course).delete()

        # Delete the course
        course_name = course.name
        course.delete()

        # Send a success message
        messages.success(request, f"Course '{course_name}' has been deleted successfully.")
        return redirect('home')  # Redirect to the home page of the dashboard
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')

