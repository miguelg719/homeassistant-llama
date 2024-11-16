FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Chromium
RUN apt-get update && apt-get install -y 

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 