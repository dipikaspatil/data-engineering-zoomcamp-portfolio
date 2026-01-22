#This builds a Python environment to run your ingestion script:

# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirement files and insall
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy data files into /data folder
RUN mkdir /data
COPY ../data/green_tripdata_2025-11.parquet /data/
COPY ../data/taxi_zone_lookup.csv /data/

# Install required packages


# Copy ingestion script
COPY ../scripts/ingest_data_hw1.py .

# Set default command
CMD ["python", "ingest_data_hw1.py"]