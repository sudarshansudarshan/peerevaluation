# Use official Python image as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /code

# Install system dependencies, including Poppler and Zbar
RUN apt-get update && apt-get install -y \
    zbar-tools \
    libzbar-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /code/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /code/

# Expose port 8000 for the Django application
EXPOSE 8000

# Set default command (optional, depending on your Django setup)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]