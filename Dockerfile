# Use an official Python runtime as a base image
FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt (if you have dependencies)
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Command to run your application
CMD ["python", "app.py"]
