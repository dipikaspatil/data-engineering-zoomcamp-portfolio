# producer.py
# -----------------------------
# Sends taxi trip data from a CSV to a Kafka/Redpanda topic
# -----------------------------

from kafka import KafkaProducer  # Kafka client library
import pandas as pd              # For reading CSV data
import json                      # For serializing messages
import time                      # Optional, to slow down sending for visibility
from models import Ride  # import Ride model
from dataclasses import asdict  # For converting dataclass to dict for JSON serialization

# -----------------------------
# 1. Connect to Kafka/Redpanda
# -----------------------------
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",          # Redpanda broker address
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Convert dict → JSON bytes
)

# -----------------------------
# 2. Load taxi CSV data
# -----------------------------
# Make sure you have 'green_tripdata_2025-10.parquet' in a 'data/' folder
df = pd.read_parquet("data/green_tripdata_2025-10.parquet")  # Load Parquet file into a DataFrame
print(f"Loaded {len(df)} taxi trip records from Parquet file green_tripdata_2025-10.parquet \n")

# -----------------------------
# 3. Send each row as a message
# -----------------------------
for _, row in df.iterrows():
    message = Ride.from_row(row)  # Convert each row to a Ride object
    message_dict = asdict(message)  # Use asdict() to convert the dataclass to a plain dict
    producer.send("green-trips", value=message_dict)  # Send to 'green-trips' topic
    print("Sent:", message)       # Optional: print confirmation
    time.sleep(0.01)              # Small delay to avoid overwhelming the broker

# -----------------------------
# 4. Flush all messages
# -----------------------------
producer.flush()  # Ensure all messages are actually sent before exiting
print("All messages sent!")