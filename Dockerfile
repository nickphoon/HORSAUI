# syntax=docker/dockerfile:1

# Use a specific Python image as the base
FROM python:3.10.7-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . /app/

# Expose the port that the Flask app will run on
EXPOSE 3000

# Run the Flask app
CMD ["python3", "-m", "flask", "--app", "main", "run", "-h", "0.0.0.0", "-p", "3000"]
