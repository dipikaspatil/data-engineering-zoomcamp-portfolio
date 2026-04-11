"""
Aviation Data Producer for Apache Flink Pipeline
--------------------------------------------
This script fetches real-time flight data from the OpenSky Network API and produces it to a Kafka topic named 'aviation_events'. 
It ensures the topic exists before producing messages and handles delivery reports for monitoring.
Key Features:
- Dynamic Topic Creation: Automatically creates the Kafka topic if it doesn't exist, following industry best practices for partitioning and replication.
- Real-Time Data Fetching: Pulls live flight data every 30 seconds, allowing for near real-time processing in the Flink pipeline.
- Robust Error Handling: Catches and logs exceptions during both topic creation and message production, ensuring stability.
- Delivery Reporting: Provides feedback on message delivery success or failure, aiding in monitoring and debugging.
Usage:
1. Ensure Kafka is running locally on port 19092.
2. Run this script to start producing aviation data to the Kafka topic.
"""
import json
import os
import time
import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

# Configuration
BOOTSTRAP_SERVERS = 'localhost:19092'
TOPIC_NAME = 'raw_aviation_data'
OPENSKY_URL = 'https://opensky-network.org/api/states/all'
remaining_credits = 100 # Default starting value, will be updated dynamically
def ensure_topic_exists():
    """Programmatically create the topic if it doesn't exist."""
    admin_client = AdminClient({'bootstrap.servers': BOOTSTRAP_SERVERS})
    
    try:
        metadata = admin_client.list_topics(timeout=5)
        if TOPIC_NAME not in metadata.topics:
            print(f"✨ Topic '{TOPIC_NAME}' not found. Creating...")
            # Industry Standard: Define partitions and replication explicitly
            new_topic = NewTopic(
                topic=TOPIC_NAME, 
                num_partitions=3,     # Allows 3 Flink workers to read in parallel
                replication_factor=1  # 1 for local dev, 3 for production
            )
            fs = admin_client.create_topics([new_topic])
            
            # Wait for creation to complete
            for topic, f in fs.items():
                f.result() 
                print(f"✅ Topic '{topic}' created successfully.")
        else:
            print(f"✔️ Topic '{TOPIC_NAME}' already exists. Ready to produce.")
    except Exception as e:
        print(f"⚠️ AdminClient error: {e}")

# Kafka Producer Instance
producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message -> {msg.topic()} [Partition: {msg.partition()}]")

def fetch_and_push():
    print("📡 Fetching data from OpenSky...")
    produced_count = 0
    try:
        response = requests.get(OPENSKY_URL, timeout=10)

        remaining_credits = int(response.headers.get('X-Rate-Limit-Remaining', 100))
        reset_time = int(response.headers.get('X-Rate-Limit-Retry-After-Seconds', 0))

        if response.status_code == 429:
            print(f"⚠️ Blocked! Must wait {reset_time} seconds.")
            time.sleep(reset_time + 1)
            return 0

        if response.status_code != 200 or not response.text.strip():
            print(f"⚠️ API issue! Status: {response.status_code}. Response was empty.")
            return 0

        try:
            data = response.json()
        except ValueError:
            print("❌ Failed to decode JSON. The API might be sending an error page.")
            return 0

        states = data.get('states', [])

        for s in states[:20]:
            if s[5] is None or s[6] is None:
                continue

            payload = {
                "icao24": s[0],
                "callsign": s[1].strip() if s[1] else "NONE",
                "origin_country": s[2],
                "timestamp": int(time.time()),
                "latitude": float(s[6]),
                "longitude": float(s[5]),
                "velocity": float(s[9]) if s[9] is not None else 0.0
            }

            wrapped_payload = {
                "sourceTopic": TOPIC_NAME,
                "payload": payload
            }

            producer.produce(
                TOPIC_NAME,
                key=payload["icao24"],
                value=json.dumps(wrapped_payload).encode("utf-8"),
                callback=delivery_report
            )
            produced_count += 1

        producer.flush()
        print(f"✅ Data Sent. Credits remaining: {remaining_credits}")
        return produced_count

    except Exception as e:
        print(f"⚠️ Producer error: {e}")
        return 0

if __name__ == "__main__":
    ensure_topic_exists() # Check/Create once at startup
    MAX_RECORDS = int(os.getenv("MAX_RECORDS", "0"))  # 0 = infinite
    count = 0
    while True:
        produced = fetch_and_push() or 0
        print("😴 Waiting 30s for next poll...")
        count += produced

        if MAX_RECORDS > 0 and count >= MAX_RECORDS:
            print(f"Produced {count} records. Exiting demo mode.")
            break

        # Dynamic Sleep: If credits are high, go fast (5s). If low, go slow (30s).
        sleep_duration = 5 if MAX_RECORDS > 0 else (30 if remaining_credits > 50 else 120)
        time.sleep(sleep_duration)