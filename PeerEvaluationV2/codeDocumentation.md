# **Documentation for Controllers in this MVC model**

## **Table of Contents**

1. [Imports](#imports)  
2. [Utility Functions](#utility-functions)  
   - [geminiGenerate](#geminigenerateprompt)  
   - [parse_llama_json](#parse_llama_jsontext)  
   - [evaluate_answers](#evaluate_answersanswer1-answer2-topic-description)  
   - [flag_evaluations_with_high_std](#flag_evaluations_with_high_stdexam_instance-request-threshold10)  
   - [is_superuser (User method override)](#is_superuserself)  
   - [is_student (User method override)](#is_studentself)  
   - [is_staff (User method override)](#is_staffself)  
   - [is_teacher (User method override)](#is_teacherself)  
   - [is_ta (User method override)](#is_taself)  
   - [generate_random_text](#generate_random_text)  
   - [convert_pdf_to_image_and_decode_qr](#convert_pdf_to_image_and_decode_qrpdf_bytes)  
   - [assign_evaluations](#assign_evaluationsstudents-papers-trusted_evaluators-k)  
3. [Views](#views)  
   - [index](#indexrequest)  
   - [pages](#pagesrequest)  
   - [course](#courserequest)  
   - [batch](#batchrequest)  
   - [download_answer_sheets](#download_answer_sheetsrequest)  
   - [enrollment](#enrollmentrequest)  
   - [ta_hub](#ta_hubrequest)  
   - [examination](#examinationrequest)  
   - [peer_evaluation](#peer_evaluationrequest)  
   - [student_eval](#student_evalrequest)  
   - [upload_evaluation](#upload_evaluationrequest)  
   - [export_evaluations_to_csv](#export_evaluations_to_csvrequest-exam_id)  
   - [topic](#topicrequest)  
   - [llm_answer](#llm_answerrequest)  
   - [documentation](#documentationrequest)  

---

## **Imports**

```python
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import is_aware
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import ExpressionWrapper, F, DateTimeField, Avg, StdDev, Q
from django.utils import timezone
import pytz
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode
from PIL import Image
import io
import tempfile
from fpdf import FPDF
import qrcode
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
```

- **Description**: The imports include Django utilities, standard libraries, and third-party libraries necessary for generating PDFs, handling peer evaluations, working with timezones, decoding QR codes, sending emails, etc.

---

## **Utility Functions**

### `geminiGenerate(prompt)`
```python
def geminiGenerate(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text
```
- **Description**:  
  Invokes the **Gemini** Generative AI model from Google’s Generative AI (`google.generativeai`) to generate text from a given prompt.

- **Parameters**:  
  - `prompt` (*str*): The text prompt to be sent to the Gemini model.

- **Returns**:  
  - (*str*): The generated text response from the model.

---

### `parse_llama_json(text)`
```python
def parse_llama_json(text):
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1

    if start_idx == -1 or end_idx == -1:
        raise ValueError("No valid JSON found in the text")

    json_part = text[start_idx:end_idx]
    try:
        parsed_data = json.loads(json_part)
        return parsed_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")
```
- **Description**:  
  Extracts JSON from a string and parses it into a Python dictionary. This is helpful for handling AI model responses that contain JSON within a larger text response.

- **Parameters**:  
  - `text` (*str*): The text that potentially contains a JSON structure.

- **Returns**:  
  - (*dict*): The parsed JSON object as a dictionary.

- **Raises**:  
  - `ValueError` if no valid JSON is found or if JSON parsing fails.

---

### `evaluate_answers(answer1, answer2, topic, description)`
```python
def evaluate_answers(answer1, answer2, topic, description):
    prompt = f"""
    ... # Omitted for brevity ...
    """
    scores = parse_llama_json(geminiGenerate(prompt))

    aggregate_score = (
        (scores['question 1']['score'] * (1 - scores['question 1']['ai'])) +
        (scores['question 2']['score'] * (1 - scores['question 2']['ai']))
    ) / 2

    return {
        "aggregate_score": round(aggregate_score, 2),
        "answers": " ".join([answer1, answer2]),
        "feedback": " ".join([scores['question 1']['feedback'], scores['question 2']['feedback']]),
        "ai_scores": [scores['question 1']['ai'], scores['question 2']['ai']],
        "scores": [scores['question 1']['score'], scores['question 2']['score']]
    }
```
- **Description**:  
  Evaluates two student answers (answer1, answer2) using an AI model (Gemini). It then parses the resulting JSON, calculates an aggregate score (penalizing AI-generated plagiarism), and returns a structured result.

- **Parameters**:  
  - `answer1` (*str*): The first student’s answer.  
  - `answer2` (*str*): The second student’s answer.  
  - `topic` (*str*): The topic title.  
  - `description` (*str*): A brief description or additional context of the topic.

- **Returns**:  
  - (*dict*): A dictionary containing the aggregate score, combined feedback, AI plagiarism scores, and individual question scores.

---

### `flag_evaluations_with_high_std(exam_instance, request, threshold=1.0)`
```python
def flag_evaluations_with_high_std(exam_instance, request, threshold=1.0):
    """
    Flags an exam instance if an evaluation's standard deviation is significantly higher
    than the average standard deviation of all evaluations.

    Parameters:
    - exam_instance: The exam instance to analyze.
    - request: Django request object (unused in logic, but can be used for messages/logging).
    - threshold: Multiplier for standard deviation; if an evaluation's deviation
      exceeds this, it's flagged.
    """
    ...
```
- **Description**:  
  Analyzes peer evaluations of a given exam and flags evaluations whose standard deviation is higher than a threshold multiplied by the global standard deviation. Also updates an incentivization scheme for evaluators who do not exceed the threshold.

- **Parameters**:  
  - `exam_instance` (*Exam*): The exam instance for which evaluations are to be analyzed.  
  - `request` (*HttpRequest*): The Django request object.  
  - `threshold` (*float*, optional): A multiplier used against the global standard deviation to determine the flagging boundary. Default is `1.0`.

- **Returns**:  
  - None  
  (*Performs actions such as updating flags and saving incentive rewards in the database.*)

---

### `is_superuser(self)`
```python
def is_superuser(self):
    return self.is_superuser
User.add_to_class('is_superuser', is_superuser)
```
- **Description**:  
  Overrides/extends the Django `User` model to add (or ensure) a `is_superuser` method. Returns whether the user is a superuser.

- **Parameters**:  
  - `self` (*User*): The user instance.

- **Returns**:  
  - (*bool*): True if the user is a superuser.

---

### `is_student(self)`
```python
def is_student(self):
    return not self.is_staff and not self.is_superuser
User.add_to_class('is_student', is_student)
```
- **Description**:  
  Determines whether a user is classified as a student. A student is neither staff nor superuser.

- **Parameters**:  
  - `self` (*User*): The user instance.

- **Returns**:  
  - (*bool*): True if the user is a student.

---

 # Documentation for Models of the project

## **Models Overview**

### **Course**
The `Course` model represents a course with its attributes and constraints.

- **Fields**:
  - `course_id` (*CharField*): Unique identifier for the course.
  - `name` (*CharField*): Name of the course.
  - `description` (*TextField*): Description of the course (optional).
  - `is_public` (*BooleanField*): Indicates if the course is publicly accessible for enrollment.
  - `start_date` (*DateTimeField*): Start date of the course.
  - `end_date` (*DateTimeField*): End date of the course.

- **Methods**:
  - `__str__`: Returns the course name.
  - `save`: Ensures no overlapping courses with the same ID are scheduled during the specified dates.

---

### **Batch**
The `Batch` model links a course to a specific batch and teacher.

- **Fields**:
  - `batch_id` (*CharField*): Unique identifier for the batch.
  - `course` (*ForeignKey*): References the associated `Course`.
  - `teacher` (*ForeignKey*): References the teacher managing the batch.

- **Meta**:
  - `unique_together`: Ensures uniqueness of the teacher for a batch in a course.

- **Methods**:
  - `__str__`: Returns a descriptive string of the batch.
  - `enrolled_students_count`: Returns the number of students enrolled in the batch.

---

### **Exam**
Represents an exam conducted for a batch.

- **Fields**:
  - `id` (*AutoField*): Primary key.
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `date` (*DateTimeField*): Date of the exam.
  - `number_of_questions` (*IntegerField*): Number of questions in the exam.
  - `duration` (*IntegerField*): Duration of the exam in minutes.
  - `max_scores` (*IntegerField*): Maximum score for the exam.
  - `k` (*IntegerField*): Number of evaluations per student.
  - `total_students` (*IntegerField*): Total number of students in the batch.
  - `completed` (*BooleanField*): Indicates if the exam is completed.
  - `flags` (*BooleanField*): Flags for evaluations.
  - `evaluations_sent` (*BooleanField*): Indicates if evaluations have been sent.

- **Methods**:
  - `__str__`: Returns the batch ID.
  - `evaluation_received`: Returns the count of documents submitted for the exam.
  - `marks_per_question`: Calculates marks per question based on total scores and questions.

---

### **UIDMapping**
Maps users to unique identifiers for exams.

- **Fields**:
  - `user` (*ForeignKey*): References the user.
  - `exam` (*ForeignKey*): Associated `Exam`.
  - `uid` (*CharField*): Unique identifier.

- **Meta**:
  - `unique_together`: Ensures uniqueness of the UID for a user.

- **Methods**:
  - `__str__`: Returns the username and UID.

---

### **Documents**
Represents documents uploaded for evaluations.

- **Fields**:
  - `uid` (*CharField*): Unique identifier for the user.
  - `exam` (*ForeignKey*): Associated `Exam`.
  - `document` (*FileField*): Path to the uploaded document.
  - `uploaded_on` (*DateTimeField*): Timestamp of upload.
  - `uploaded_by` (*ForeignKey*): User who uploaded the document.

---

### **PeerEvaluation**
Represents peer evaluations conducted by students.

- **Fields**:
  - `evaluator` (*ForeignKey*): The user performing the evaluation.
  - `evaluated_on` (*DateTimeField*): Timestamp of evaluation.
  - `deadline` (*DateTimeField*): Deadline for completing the evaluation.
  - `uid` (*CharField*): Unique identifier for the user.
  - `student` (*ForeignKey*): The user being evaluated.
  - `exam` (*ForeignKey*): Associated `Exam`.
  - `document` (*ForeignKey*): Associated `Documents`.
  - `feedback` (*TextField*): Feedback provided.
  - `ticket` (*IntegerField*): Ticket for evaluation.
  - `score` (*TextField*): Score assigned during evaluation.

- **Properties**:
  - `get_score`: Parses and returns the score as a list.
  - `get_score_string`: Returns a formatted string of scores.
  - `total`: Calculates the total score.

---

### **Statistics**
Stores statistical data for a batch.

- **Fields**:
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `avg_score` (*FloatField*): Average score.
  - `std_dev` (*FloatField*): Standard deviation of scores.

- **Methods**:
  - `__str__`: Returns a string describing the statistics for a batch.

---

### **Incentivization**
Tracks rewards and incentives for students in a batch.

- **Fields**:
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `student` (*ForeignKey*): The student being incentivized.
  - `rewards` (*FloatField*): Rewards for the student.
  - `exam_count` (*IntegerField*): Number of exams attempted by the student.

- **Meta**:
  - `unique_together`: Ensures no duplicate entries for a student in a batch.

- **Methods**:
  - `__str__`: Returns a string describing the rewards and batch.

---

### **StudentEnrollment**
Handles student enrollment in batches and courses.

- **Fields**:
  - `student` (*ForeignKey*): The student.
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `course` (*ForeignKey*): Associated `Course`.
  - `approval_status` (*BooleanField*): Indicates if the enrollment is approved.

- **Meta**:
  - `unique_together`: Ensures uniqueness of enrollment requests for a student and course.

- **Methods**:
  - `save`: Prevents duplicate enrollment requests.
  - `__str__`: Returns the student username.

---

### **TeachingAssistantAssociation**
Associates teaching assistants (TAs) with batches.

- **Fields**:
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `teaching_assistant` (*ForeignKey*): The TA.

- **Meta**:
  - `unique_together`: Ensures a TA is not assigned to the same batch multiple times.

- **Methods**:
  - `__str__`: Returns a string of the TA and batch.
  - `is_ta`: Static method to check if a user is a TA for a specific batch.

---

### **CourseTopic**
Represents topics covered in a course.

- **Fields**:
  - `id` (*AutoField*): Primary key.
  - `course` (*ForeignKey*): Associated `Course`.
  - `batch` (*ForeignKey*): Associated `Batch`.
  - `topic` (*CharField*): Name of the topic.
  - `description` (*TextField*): Description of the topic.
  - `date` (*DateField*): Date when the topic is covered.

- **Methods**:
  - `__str__`: Returns the topic name.

---

### **LLMEvaluation**
Handles evaluations using Large Language Models (LLM).

- **Fields**:
  - `Topic` (*ForeignKey*): Associated `CourseTopic`.
  - `student` (*ForeignKey*): The student.
  - `answer` (*TextField*): Student's response.
  - `feedback` (*TextField*): Feedback provided.
  - `score` (*TextField*): Score assigned.
  - `ai` (*TextField*): AI evaluation data.
  - `aggregate` (*IntegerField*): Aggregate score.
  - `date` (*DateTimeField*): Date of evaluation.

- **Methods**:
  - `__str__`: Returns a string describing the LLM evaluation for a student.


