# Peer Evaluation 
## Features
### Core Functionalities
- **Evaluation through QR code:** The peer evaluation software can evaluate and detect QR on the answer sheets and map it to the peers for peer evaluation. This not only keeps the privacy of the students, whose papers they are correcting
 but also makes the paper distribution process more secure and accurate.
- **Automated student to UID mapping:** As the student uploads their answer scripts, the answer scripts are automatically mapped to the student's account and also to their mail ID with the unique ID of the answer script.
- **The User interface:** The UI of this version of peer evaluation is easy to navigate for both professors and students and more smooth on both mobile web and desktop web.
- **The Analytics:** As the peer evaluation goes on the professor can see all the details of markings and students in graphical form, this is to give insights on mean marks and standard deviation.
- **LLM Integration for daily evaluation:** LLM generates 2 questions each day and asks students to answer those two questions this makes a robust learning environment along with corrections for incorrect answers.
- **Feedback and Raise Ticket:** During the evaluation the student can give feedback for each answer they have given marks. In case any student is unsatisfied of the marks or the feedback or faces any kind of issue, they can raise ticket for the same.

## Installation

## Prerequisites
1. **Git**: For cloning the repository.
2. **Python**: Version 3.8 or higher.
3. **pip**: For managing Python packages.
4. **Virtual Environment**: Recommended to avoid conflicts.
5. **Docker** (Optional): For containerized deployment.

---

### Step 1: Install Prerequisites
- Install Git, Python, and pip as per your operating system.
- Optionally, install Docker if you prefer a containerized setup (instructions included above).

---

### Step 2: Clone the Repository
1. Open a terminal or command prompt.
2. Clone the repository:
   ```bash
   git clone https://github.com/sudarshansudarshan/peerevaluation.git
   ```
3. Navigate to the project directory:
   ```bash
   cd peerevaluation/PeerEvaluationV2
   ```

---

### Step 3: Set Up the Local Environment
1. **Create and activate a virtual environment**:
   - On Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 4: Configure the Django Application
1. **Set up the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
2. **Create a superuser** (admin account):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set up a username, email, and password.

3. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```
   This command gathers all static assets into a single location for use by the application.

---

### Step 5: Run the Django Application Locally
1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Access the application in your web browser at:
   ```
   http://127.0.0.1:8000
   ```

---

### Step 6: Test the Application
1. Log in to the admin panel:
   - Navigate to: `http://127.0.0.1:8000/admin`
   - Use the credentials created with `createsuperuser`.
2. Test the application functionality:
   - Use the default test account if provided:
     - **Username**: `admin@gmail.com`
     - **Password**: `Abcd@1234`

---

### Optional: Running with Docker
Follow the Docker instructions outlined previously if you prefer a containerized setup.


## Structure of Repository
```
PeerEvaluationV2/
├── manage.py               # Django project management script
├── requirements.txt        # List of Python dependencies
├── Dockerfile              # Docker configuration file (if applicable)
├── docker-compose.yml      # Docker Compose configuration (if applicable)
├── README.md               # Project documentation (if available)
├── static/                 # Static files (CSS, JS, images)
│   └── ...                 # Static assets for the project
├── media/                  # Media files (uploaded by users)
│   └── ...                 # Uploaded content
├── templates/              # HTML templates for the application
│   └── ...                 # Application-specific templates
├── .env                    # Environment variables (not included in the repo for security)
├── app_name/               # Main Django app directory
│   ├── __init__.py         # App initialization file
│   ├── admin.py            # Django admin customization
│   ├── apps.py             # App configuration
│   ├── models.py           # Database models
│   ├── views.py            # Views handling HTTP requests
│   ├── urls.py             # URL routing for the app
│   ├── forms.py            # Django forms (if applicable)
│   ├── serializers.py      # API serializers (if applicable)
│   ├── tests.py            # Unit tests for the app
│   └── migrations/         # Database migrations
│       ├── __init__.py     # Migration initialization
│       └── ...             # Individual migration files
├── project_name/           # Project-level directory
│   ├── __init__.py         # Project initialization file
│   ├── asgi.py             # ASGI configuration
│   ├── settings.py         # Django project settings
│   ├── urls.py             # Project-level URL routing
│   └── wsgi.py             # WSGI configuration for deployment
└── tests/                  # Project-wide tests (optional)
    └── ...                 # Additional test modules
└── README.md               # Project Documentation
```
