# Peer Evaluation System

The **Peer Evaluation System** is a reliable and scalable solution designed to enhance the learning experience in large class sizes. This system facilitates fair and efficient assessment by leveraging peer feedback, enabling participants to evaluate each other's work under structured guidelines. The system allows teachers to track student learning outside the class without any extra workload.

---

## Features

### Core Functionalities
* **Automated File Mapping (OCR):** Files are renamed using the number from the top-left corner and mapped to the student with the corresponding unique ID for the current exam.
* **Automated File Distribution:** Files are automatically distributed to students for evaluation based on class size or the number of students who appeared in the exam.
* **Tiered Ticket Raising:** A tiered ticketing system for peer evaluation, allowing issues to be escalated based on complexity.

---

## Installation and Setup

### Prerequisites
The application has been Dockerized, meaning Docker will handle all dependencies. The only prerequisite is **Git** to clone the repository.

Below are the instructions for installing Git and Docker on various platforms.

---

### Step 1: Install Git

#### On Ubuntu (Linux):
1. Open a terminal.
2. Run:
   ```bash
   sudo apt update
   sudo apt install -y git
   ```
3. Verify installation:
   ```bash
   git --version
   ```

#### On macOS:
1. Open a terminal.
2. Install Git using Homebrew:
   ```bash
   brew install git
   ```
3. Verify installation:
   ```bash
   git --version
   ```

#### On Windows:
1. Download the [Git installer](https://git-scm.com/downloads).
2. Run the installer and follow the setup wizard.
3. Verify installation by opening the Command Prompt and running:
   ```cmd
   git --version
   ```

---

### Step 2: Install Docker

#### On Ubuntu:
Run the following script to install Docker:
```bash
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting the setup process..."

# Step 0: Install dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository to Apt sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index and install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker-compose --version
```

#### On macOS:
1. Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/).
2. Follow the installation instructions and launch Docker Desktop.
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

#### On Windows:
1. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
2. Ensure "WSL 2" is enabled during the installation process.
3. Launch Docker Desktop.
4. Verify installation by running in Command Prompt or PowerShell:
   ```cmd
   docker --version
   docker-compose --version
   ```

---

### Step 3: Run the Application

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sudarshansudarshan/peerevaluation.git
   cd peerevaluation
   cd PeerEvaluationV1
   ```

2. **Run the Application Using Docker**

   #### On Windows:

   Execute the following commands to build and start the application:
   ```cmd
   docker-compose up --build
   ```

   #### On MacOS / Linux:


   Execute the following commands to build and start the application:
   ```bash
   sudo docker-compose down || true
   sudo docker-compose up --build
   ```

   This will:
   - Build the Docker images.
   - Start the containers with all dependencies pre-configured.

3. **Test the app**

   For testing purposes, the default access provided would be an **Admin** role
   For which:-
   Username (Default): admin
   Password (Default): Abcd@1234

   The 'Teacher' role can be accessed by registering on the registration page and then update the role from default Admin ID.

---

## Documentation
For detailed documentation and guides, refer to the PDF files in the **Documentation** folder of the repository.

---

## Troubleshooting

If you encounter any issues during setup, ensure:
1. Git and Docker are correctly installed.
2. Docker is running.
3. You have sufficient permissions to execute Docker commands (use `sudo` if necessary).

---

For inquiries, feedback, or suggestions, feel free to:
* Open an issue on the repository.
* Reach out to the maintainers at:
  - ashu.kaushik@iitrpr.ac.in
  - rohit.24csz0014@iitrpr.ac.in

--- 
