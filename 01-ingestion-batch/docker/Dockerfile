#This builds a Python environment to run your ingestion script:

# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ingestion script
COPY scripts/ingest_data.py .

# Set default command
CMD ["python", "ingest_data.py"]
