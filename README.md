# Peer Evaluation System
The **Peer Evaluation System** is a reliable and scalable solution designed to enhance the learning experience in large class sizes. This system facilitates fair and efficient assessment by leveraging peer feedback, enabling participants to evaluate each other's work under structured guidelines. The system allows teachers to keep track of student learning outside the class without any extra workload.

---

## Features
### Core Functionalities
* **Automated File Mapping(OCR):** The file is renamed using the number from the top-left corner of the file, and then it is mapped to the student whose unique ID corresponds to it for the current exam.
* **Automated File Distribution:** The files are automatically sent to the students for evaluation based on the class size or the number of students who appeared in the exam.
* **Tiered Ticket Raising:** Enable a tiered ticketing system for peer evaluation, allowing issues to be escalated based on complexity.

---

# Installation and Setup
## Prerequisites
To set up the software for development, the following tools are required:

* VSCode: For easy development environment.
* PostgreSQL: For data storage.
* Git: For cloning repository.
* Tesseract OCR in environment paths.
* Poppler library in environment paths.

## Steps
1. Clone the Repository
   ```
   git clone https://github.com/sudarshansudarshan/peerevaluation.git
   cd peerevaluation
   cd PeerEvaluationV1
   ```

2. Set Up settings.py of peereval
   * Add your PostgreSQL credentials in the Database section (line 78) of the file, or use the credentials there to set up the environment on your system.
   * Add your email details in the email configuration section near line 143 to send emails from your email ID.

3. Run application using
   * Navigate to the folder where manage.py is located using cd <folder_name>, and run the commands provided below.
   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

---
## Documentation
For more detailed documentation and guides, refer to the PDF files present in the Documentation folder of the Repository.

---
For any inquiries, feedback, or suggestions, feel free to:
* Open an issue on the repository.
* Reach out to the maintainers at ashu.kaushik@iitrpr.ac.in or at rohit.24csz0014@iitrpr.ac.in.
