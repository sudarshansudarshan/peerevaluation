#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting the setup process..."

# Step 0: Install Git
echo "Installing Git..."
sudo apt-get update
sudo apt-get install -y git

# Step 1: Clone the Git repository
echo "Cloning the repository..."
if [ ! -d "peerevaluation" ]; then
  git clone https://github.com/sudarshansudarshan/peerevaluation.git
else
  echo "Repository already exists. Skipping clone."
fi

# Step 2: Navigate to the project directory
cd peerevaluation/PeerEvaluationV1

# Step 3: Install Docker
echo "Installing Docker..."

# Add Docker's official GPG key
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository to Apt sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index and install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin