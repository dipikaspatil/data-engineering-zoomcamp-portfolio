import json
import os
import time
import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

TOPIC_NAME = "raw_geo_data"
BOOTSTRAP_SERVERS = "localhost:19092"
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
POLL_INTERVAL_SECONDS = 300

print(f"🚀 Starting Geo Producer on topic '{TOPIC_NAME}'...")

def ensure_topic_exists():
    print(f"🔍 Checking if topic exists {TOPIC_NAME}")
    admin_client = AdminClient({"bootstrap.servers": BOOTSTRAP_SERVERS})

    try:
        print("⏳ Checking topic metadata...")
        metadata = admin_client.list_topics(timeout=5)
        if TOPIC_NAME not in metadata.topics:
            print(f"✨ Topic '{TOPIC_NAME}' not found. Creating...")
            new_topic = NewTopic(
                TOPIC_NAME,
                num_partitions=3,
                replication_factor=1
            )
            futures = admin_client.create_topics([new_topic])

            for topic, future in futures.items():
                future.result()
                print(f"✅ Topic '{topic}' created successfully.")
        else:
            print(f"✔️ Topic '{TOPIC_NAME}' already exists.")
    except Exception as e:
        print(f"⚠️ Topic setup error: {e}")

producer = Producer({
    "bootstrap.servers": BOOTSTRAP_SERVERS
})

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for key={msg.key()}: {err}")
    else:
        print(f"✅ Message -> {msg.topic()} [partition={msg.partition()} offset={msg.offset()}]")

seen_events = set()

def fetch_and_push():
    global seen_events
    print(f"📡 Fetching data from {USGS_URL}...")

    try:
        response = requests.get(USGS_URL, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ USGS returned HTTP {response.status_code}")
            return 0

        data = response.json()
        features = data.get("features", [])

        new_count = 0

        for feature in features:
            event_id = feature.get("id")
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [])

            if not event_id:
                continue

            if event_id in seen_events:
                continue

            if len(coordinates) < 3:
                print(f"⚠️ Skipping event {event_id}: invalid coordinates")
                continue

            event_time_ms = properties.get("time")
            if event_time_ms is None:
                print(f"⚠️ Skipping event {event_id}: missing time")
                continue

            geo_record = {
                "id": event_id,
                "mag": properties.get("mag") if properties.get("mag") is not None else 0.0,
                "place": properties.get("place", "Unknown"),
                "timestamp": int(event_time_ms / 1000),
                "lon": coordinates[0],
                "lat": coordinates[1],
                "depth": coordinates[2],
            }

            wrapped_payload = {
                "sourceTopic": TOPIC_NAME,
                "payload": geo_record
            }

            producer.produce(
                TOPIC_NAME,
                key=event_id,
                value=json.dumps(wrapped_payload).encode("utf-8"),
                callback=delivery_report,
            )
            producer.poll(0)

            seen_events.add(event_id)
            new_count += 1

        print(f"📊 Fetched {len(features)} events, {new_count} new events to produce.")
        producer.flush()
        print(f"🚀 Pushed {new_count} new events to Kafka.")

        if len(seen_events) > 5000:
            print("🧹 Resetting seen_events cache.")
            seen_events = set(list(seen_events)[-2000:])

        return new_count

    except Exception as e:
        print(f"⚠️ Producer error: {e}")
        return 0

if __name__ == "__main__":
    ensure_topic_exists()
    MAX_RECORDS = int(os.getenv("MAX_RECORDS", "0"))
    MAX_EMPTY_POLLS = int(os.getenv("MAX_EMPTY_POLLS", "3"))

    count = 0
    empty_polls = 0

    while True:
        produced = fetch_and_push() or 0
        count += produced

        if MAX_RECORDS > 0:
            if produced == 0:
                empty_polls += 1
                print(f"🟡 No new events this poll ({empty_polls}/{MAX_EMPTY_POLLS})")
            else:
                empty_polls = 0

            if count >= MAX_RECORDS:
                print(f"✅ Produced {count} records. Exiting demo mode.")
                break

            if empty_polls >= MAX_EMPTY_POLLS:
                print(f"🛑 No new events after {empty_polls} consecutive demo polls. Produced {count} total records. Exiting demo mode.")
                break

        sleep_duration = 5 if MAX_RECORDS > 0 else POLL_INTERVAL_SECONDS
        print(f"😴 Waiting {sleep_duration}s for next poll...")
        time.sleep(sleep_duration)