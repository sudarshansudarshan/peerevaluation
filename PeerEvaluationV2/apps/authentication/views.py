# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm, PasswordResetForm
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.core.mail import send_mail
import random
import array
from django.contrib import messages

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


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def forgetPassword(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            # Get the email from the form
            email = form.cleaned_data['email']
            
            # Fetch the user based on the email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # If user doesn't exist, show an error message
                messages.error(request, 'User with this email not found.')
                return redirect('forgetPassword')  # Redirect to the same page
            
            # Generate a new random password
            new_password = generate_password(10)

            # Create the email content
            html_message = render_to_string(
                "accounts/changePassword.html",  # Path to your email template
                {
                    "username": user.username,
                    "new_password": new_password
                },
            )
            plain_message = strip_tags(html_message)  # Fallback plain text version

            # Send the email with the new password
            send_mail(
                subject="Peer Evaluation Forget Password credentials",
                message=plain_message,
                from_email="no-reply@evaluation-system.com",
                recipient_list=[user.email],
                html_message=html_message,  # Attach the HTML message
                fail_silently=False,
            )

            # Update the user's password in the system
            user.set_password(new_password)
            user.save()

            # Notify the user that an email was sent
            messages.success(request, 'Password reset email sent successfully!')
            return redirect('/login/')  # Redirect to login page after resetting

    else:
        form = PasswordResetForm()

    return render(request, 'accounts/forgetPassword.html', {'form': form})