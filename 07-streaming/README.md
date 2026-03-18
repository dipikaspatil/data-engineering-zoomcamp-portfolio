## Homework - Stream Processing

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/07-streaming/homework.md

In this homework, we'll practice streaming with Kafka (Redpanda) and PyFlink.

We use Redpanda, a drop-in replacement for Kafka. It implements the same protocol, so any Kafka client library works with it unchanged.

For this homework we will be using Green Taxi Trip data from October 2025:

green_tripdata_2025-10.parquet

## Project Structure (Create your own)

```
hw7
│
├── docker-compose.yml
├── producer.py
├── consumer.py
├── data
│   └── green_tripdata.csv
└── requirements.txt
```

## Docker Compose (Kafka / Redpanda)

Create docker-compose.yml

## Start services:

```bash
docker compose up -d
```

Logs - 

```logs
docker compose up -d
[+] Running 14/14
 ✔ redpanda Pulled                                                                                                                                                                                        15.8s
   ✔ 3fb9a54c97d6 Pull complete                                                                                                                                                                           14.5s
   ✔ c755d3b9ae88 Pull complete                                                                                                                                                                            2.4s
   ✔ ae346c002ed8 Pull complete                                                                                                                                                                            0.8s
   ✔ f9d5f4b0860d Pull complete                                                                                                                                                                            3.9s
   ✔ 04cb0c6e88ad Pull complete                                                                                                                                                                            2.5s
 ✔ kafka-ui Pulled                                                                                                                                                                                        10.1s
   ✔ 20ccf3e8431f Pull complete                                                                                                                                                                            0.2s
   ✔ 60a00c11adf5 Pull complete                                                                                                                                                                            0.7s
   ✔ 98eca93caa9b Pull complete                                                                                                                                                                            0.4s
   ✔ 4f27eecc6d58 Pull complete                                                                                                                                                                            8.9s
   ✔ c2fb3a8026b6 Pull complete                                                                                                                                                                            0.4s
   ✔ 198908454131 Pull complete                                                                                                                                                                            7.4s
   ✔ 0837c055c278 Pull complete                                                                                                                                                                            0.4s
[+] Running 3/3
 ✔ Network hw7_default       Created                                                                                                                                                                       0.1s
 ✔ Container redpanda        Started                                                                                                                                                                       1.0s
 ✔ Container hw7-kafka-ui-1  Started
 ```

## Open UI:

```
http://localhost:8080
```
![Kafka UI](../hw7/images/kafka_ui.png)

## Install Python Dependencies

Create requirements.txt

```
kafka-python
pandas
```

Install

```
pip install -r requirements.txt
```

## Create Kafka Topic

Run:

```bash
docker exec -it redpanda rpk topic create green-trips
```

Output - 
```bash
TOPIC        STATUS
green-trips  OK
```

Breakdown:

- `docker exec` : Runs a command inside a running container.
    - Syntax: docker exec [options] <container_name> <command>
- `-it`
    - -i → interactive mode (keeps STDIN open)
    - -t → allocates a pseudo-TTY (makes it behave like a terminal)

Together, they let you run commands interactively inside the container.

- `redpanda` - This is the name of the container where Redpanda is running (container_name: redpanda in docker-compose).

- `rpk topic create green-trips`
    - rpk is Redpanda’s CLI tool (like Kafka’s kafka-topics.sh).
    - topic create → creates a new Kafka topic.
    - green-trips → the name of the topic you’re creating.

`✅ Result: Redpanda creates a new topic called green-trips where your producer can send messages.`

Check:

```bash
docker exec -it redpanda rpk topic list
```

Output
```bash
NAME         PARTITIONS  REPLICAS
green-trips  1           1
```

- `rpk topic list` → asks Redpanda to show all existing topics.

## Kafka data streaming flowchart for taxi trips

![Flowchart](../hw7/images/Kafka_data_streaming_flowchart_for_taxi_trips.png)

## Producer (Send Taxi Data)

Create producer.py

### ✅ Key Comments / Explanations

- KafkaProducer
    - Connects to Redpanda/Kafka broker.
    - bootstrap_servers → broker address.
    - value_serializer → convert Python dict to bytes; Kafka only sends bytes.
- Reading CSV
    - pandas reads your taxi CSV into a DataFrame.
    - Each row represents one trip.
- Sending messages
    - producer.send(topic, value=...) → puts a message on the topic.
    - Each row becomes one Kafka message.
- Flush
    - Ensures that all messages are sent before the program exits.
    - Important in streaming/production to avoid losing messages.
- Optional time.sleep
    - Makes the output readable in terminal.
    - In production, you can remove it to maximize throughput.

### Run

```bash
python producer.py
```

Now messages go into Kafka topic.

## Consumer (Read Messages)

Create consumer.py

### Run:
```bash
python consumer.py
```

- Consumer connects to broker - Redpanda container exposed by Docker.
- Consumer subscribes to topic green-trips
- Consumer waits for messages
    - Kafka consumers continuously poll the broker.
```
Producer → Topic → Consumer
```
- As soon as the producer sends a message, the consumer prints it.
```
Consumer started... waiting for messages

Received message:
{'VendorID': 2, 'lpep_pickup_datetime': '2020-01-01 00:03:00', ...}
----------------------------------
```

```
localhost:9092
```

## Verify in Kafka UI

### Open:
```
localhost:8080
```

### Navigate:
```
Clusters → redpanda → Topics → green-trips
```

### We can see:

- message count
- partition
- offsets

## Important concepts

- Serialization / Deserialization
    - Producer: dict → JSON → bytes
    - Consumer: bytes → JSON → dict

- Consumer groups - group_id="taxi-consumer-group"
    - If you start multiple consumers with the same group, Kafka distributes messages across them.
    ```
    Consumer A  ← partition 0
    Consumer B  ← partition 1
    ```
- Offsets
    - Kafka tracks how far the consumer has read.
    ```
    offset 0
    offset 1
    offset 2
    ...
    ```
    - If the consumer restarts, it continues from the last committed offset.

## Full local streaming pipeline

```
Taxi CSV
   │
   ▼
producer.py
   │
   ▼
Redpanda Topic (green-trips)
   │
   ▼
consumer.py
```


## Homework Questions