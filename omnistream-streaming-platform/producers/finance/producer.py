import json
import os
import time
import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / "docker/.env"

print(f"Looking for .env at: {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH)

TOPIC_NAME = "raw_finance_data"
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS_EXTERNAL", "localhost:19092")
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

SYMBOLS = os.getenv("FINANCE_SYMBOLS", "IBM,AAPL,MSFT").split(",")
SYMBOLS = [s.strip() for s in SYMBOLS if s.strip()]

POLL_INTERVAL_SECONDS = 60
DEMO_POLL_INTERVAL_SECONDS = 15
SYMBOL_DELAY_SECONDS = float(os.getenv("FINANCE_SYMBOL_DELAY_SECONDS", "12"))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

if not DEMO_MODE and not API_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY environment variable is not set")

print(
    f"🚀 Starting Finance Producer on topic '{TOPIC_NAME}' "
    f"for symbols {SYMBOLS} (DEMO_MODE={DEMO_MODE})..."
)


def ensure_topic_exists():
    admin_client = AdminClient({"bootstrap.servers": BOOTSTRAP_SERVERS})

    try:
        metadata = admin_client.list_topics(timeout=5)
        if TOPIC_NAME not in metadata.topics:
            print(f"✨ Topic '{TOPIC_NAME}' not found. Creating...")
            new_topic = NewTopic(
                topic=TOPIC_NAME,
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
        print(f"⚠️ AdminClient error: {e}")


producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Message delivered to {msg.topic()} "
            f"[partition={msg.partition()} offset={msg.offset()}]"
        )


last_prices = {}


def fetch_quote(symbol):
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "Note" in data:
        print(f"⚠️ API limit reached for {symbol}: {data['Note']}")
        return None

    if "Information" in data:
        print(f"⚠️ API info/limit for {symbol}: {data['Information']}")
        return None

    if "Error Message" in data:
        print(f"⚠️ API error for {symbol}: {data['Error Message']}")
        return None

    quote = data.get("Global Quote")
    if not quote or "01. symbol" not in quote:
        print(f"⚠️ No valid quote found for {symbol}. Raw response: {data}")
        return None

    return quote


def build_demo_records():
    now = int(time.time())
    return [
        {
            "symbol": "IBM",
            "price": 246.74,
            "volume": 1000000,
            "timestamp": now,
            "change_percent": "0.42%"
        },
        {
            "symbol": "AAPL",
            "price": 189.12,
            "volume": 1500000,
            "timestamp": now,
            "change_percent": "0.31%"
        },
        {
            "symbol": "MSFT",
            "price": 425.55,
            "volume": 900000,
            "timestamp": now,
            "change_percent": "-0.18%"
        }
    ]


def produce_record(finance_record):
    wrapped_payload = {
        "sourceTopic": TOPIC_NAME,
        "payload": finance_record
    }

    producer.produce(
        TOPIC_NAME,
        key=finance_record["symbol"],
        value=json.dumps(wrapped_payload).encode("utf-8"),
        callback=delivery_report
    )
    producer.poll(0)


def fetch_and_push():
    if DEMO_MODE:
        produced_count = 0
        for record in build_demo_records():
            produce_record(record)
            produced_count += 1
            print(f"📈 Sent demo market data: {record}")
        producer.flush()
        return produced_count

    produced_count = 0

    for idx, symbol in enumerate(SYMBOLS):
        try:
            print(f"📡 Fetching data for {symbol}...")
            quote = fetch_quote(symbol)

            if not quote:
                if idx < len(SYMBOLS) - 1:
                    print(f"⏳ Sleeping {SYMBOL_DELAY_SECONDS}s before next symbol...")
                    time.sleep(SYMBOL_DELAY_SECONDS)
                continue

            current_price = float(quote["05. price"])
            previous_price = last_prices.get(symbol)

            if previous_price is not None and current_price == previous_price:
                print(f"😴 Price for {symbol} unchanged (${current_price}). Skipping.")
            else:
                finance_record = {
                    "symbol": quote["01. symbol"],
                    "price": current_price,
                    "volume": int(quote["06. volume"]),
                    "timestamp": int(time.time()),
                    "change_percent": quote["10. change percent"]
                }

                produce_record(finance_record)

                last_prices[symbol] = current_price
                produced_count += 1
                print(f"📈 Sent market data: {finance_record}")

        except Exception as e:
            print(f"⚠️ Producer error for {symbol}: {e}")

        if idx < len(SYMBOLS) - 1:
            print(f"⏳ Sleeping {SYMBOL_DELAY_SECONDS}s before next symbol...")
            time.sleep(SYMBOL_DELAY_SECONDS)

    producer.flush()
    return produced_count


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
                print(f"🟡 No new finance records this poll ({empty_polls}/{MAX_EMPTY_POLLS})")
            else:
                empty_polls = 0

            if count >= MAX_RECORDS:
                print(f"✅ Produced {count} records. Exiting demo mode.")
                break

            if empty_polls >= MAX_EMPTY_POLLS:
                print(
                    f"🛑 No new finance records after {empty_polls} consecutive demo polls. "
                    f"Produced {count} total records. Exiting demo mode."
                )
                break

        sleep_duration = DEMO_POLL_INTERVAL_SECONDS if MAX_RECORDS > 0 else POLL_INTERVAL_SECONDS
        print(f"😴 Waiting {sleep_duration}s for next poll...")
        time.sleep(sleep_duration)