import pandas as pd
import json
from time import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

# 1. Create Topic (if not exists)
admin_client = KafkaAdminClient(bootstrap_servers="localhost:19092")  # Connect to Redpanda's external listener
topic_name = "green-trips"

# Optional: Delete if exists
try:
    admin_client.delete_topics(topics=[topic_name])
    print(f"Topic {topic_name} deleted.")
except Exception:
    pass 

# Create new
try:
    admin_client.create_topics(new_topics=[NewTopic(name=topic_name, num_partitions=1, replication_factor=1)])
    print(f"Topic {topic_name} created.")
except TopicAlreadyExistsError:
    print(f"Topic {topic_name} already exists.")

# 2. Setup Producer
producer = KafkaProducer(
    bootstrap_servers="localhost:19092",  # Use Redpanda's external listener
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# 3. Load and Filter Data
df = pd.read_parquet("data/green_tripdata_2025-10.parquet")

# Requirement: Keep only specific columns
required_columns = [
    'lpep_pickup_datetime',
    'lpep_dropoff_datetime',
    'PULocationID',
    'DOLocationID',
    'passenger_count',
    'trip_distance',
    'tip_amount',
    'total_amount'
]
df = df[required_columns]

# 4. Measure Time and Send
t0 = time()

for row in df.itertuples(index=False):
    # Requirement: Convert row to dict
    row_dict = row._asdict()
    
    # Requirement: Convert datetimes to strings
    row_dict['lpep_pickup_datetime'] = str(row_dict['lpep_pickup_datetime'])
    row_dict['lpep_dropoff_datetime'] = str(row_dict['lpep_dropoff_datetime'])
    
    producer.send("green-trips", value=row_dict)

producer.flush()
t1 = time()

print(f'took {(t1 - t0):.2f} seconds')