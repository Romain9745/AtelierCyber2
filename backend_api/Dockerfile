# Use an official Python image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY /app/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY ./app .

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Define the command to run your FastAPI app
CMD ["fastapi", "run", "main.py", "--port", "8000"]