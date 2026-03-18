from kafka import KafkaConsumer
import json

# 1. Create Kafka Consumer
consumer = KafkaConsumer(
    "green-trips",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="homework-check-group_3",
    # Set a timeout so the script finishes when no more messages arrive
    consumer_timeout_ms=10000 
)

print("Consumer started... counting trips where distance > 5.0")

count = 0

try:
    for message in consumer:
        # The data is now a dictionary (as sent by your updated producer)
        trip = message.value
        
        # Check the condition
        if float(trip.get('trip_distance', 0)) > 5.0:
            count += 1
            
except Exception as e:
    print(f"Error: {e}")

print(f"\nFinal Count: {count}")
consumer.close()