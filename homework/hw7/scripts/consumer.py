# consumer.py
# -------------------------------------------
# Kafka / Redpanda Consumer
# Reads taxi trip messages from the topic
# -------------------------------------------

from kafka import KafkaConsumer   # Kafka client library
import json                       # Used for deserializing JSON messages
from models import Ride  # import Ride model (optional, if you want to convert dicts back to Ride objects)


# -------------------------------------------
# 1. Create Kafka Consumer
# -------------------------------------------
consumer = KafkaConsumer(
    "green-trips",                      # Topic name to subscribe to
    bootstrap_servers="localhost:9092", # Address of Redpanda broker
    value_deserializer=lambda x: json.loads(x.decode("utf-8")), # Deserializer converts raw bytes from Kafka → Python dictionary
    auto_offset_reset="earliest", # Start reading from earliest message if no committed offset exists
    enable_auto_commit=True, # Automatically commit offsets (track how far we have read)
    group_id="taxi-consumer-group" # Consumer group name
)


# -------------------------------------------
# 2. Start listening for messages
# -------------------------------------------
print("Consumer started... waiting for messages\n")

# KafkaConsumer acts like an iterator that yields messages continuously
for message in consumer:

    # Each message has metadata + the actual value
    # message.value is already deserialized because of value_deserializer
    message = message.value

    # Convert the dictionary back to a Ride object
    trip_data = Ride(**message)  # Unpack dictionary into Ride constructor
    # Convert pickup time to human-readable format
    readable_date = trip_data.pickup_datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    # Print the taxi trip data    
    print(f"Received Trip at: {readable_date}")
    print(f"From Location: {trip_data.PULocationID} to {trip_data.DOLocationID}")
    print(f"Total Amount: ${trip_data.total_amount:.2f}")
    print("----------------------------------")


# -------------------------------------------
# 3. (Optional) Close consumer when finished
# -------------------------------------------
# consumer.close()