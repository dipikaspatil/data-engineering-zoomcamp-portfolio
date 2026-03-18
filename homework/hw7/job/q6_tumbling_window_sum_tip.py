"""
This script sets up a Flink streaming job that reads from a Kafka topic containing green taxi trip data, 
processes the data using tumbling windows to calculate the total tip amount for each hour, 
and writes the results to a PostgreSQL database. 
The script also includes logging for better visibility into the job's execution and ensures that the necessary 
Postgres table exists before starting the Flink job.
"""
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

import psycopg2
import time

import logging
import sys

# Setup standard Python logging to output to your terminal
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the Postgres table exists before starting the Flink job
def ensure_postgres_table():
    logger.info("Ensuring Postgres table 'hourly_tip_totals' exists...")
    """Verify or create the Postgres sink table before Flink starts."""
    # Retry loop because Postgres might take a few seconds to accept connections
    for i in range(10):
        try:
            # Attempt to connect to Postgres and create the table if it doesn't exist
            logger.info(f"Attempting to connect to Postgres (attempt {i+1}/10)...")
            conn = psycopg2.connect(
                host="postgres",
                database="taxi_db",
                user="postgres",
                password="password",
                connect_timeout=5
            )
            cur = conn.cursor()
            # Creating the actual table Flink expects
            logger.info("Connected to Postgres, creating table if it doesn't exist...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS hourly_tip_totals (
                    window_start TIMESTAMP(3),
                    window_end TIMESTAMP(3),
                    total_tip_amount DOUBLE PRECISION
                );
            """)
            conn.commit()
            cur.close()
            conn.close()

            logger.info("Successfully verified/created Postgres table - hourly_tip_totals.")
            return
        except Exception as e:
            logger.error(f"Postgres not ready yet (attempt {i+1}/10): {e}")
            time.sleep(2)
    raise Exception("Could not connect to Postgres after 10 attempts.")

def run_tumbling_window_job():
    logger.info("Starting Flink job to process tumbling windows...")
    # 1. Environment Setup
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(environment_settings=settings)
    # Important for Watermarks to progress on a 1-partition topic
    t_env.get_config().get_configuration().set_string("parallelism.default", "1")

    # Add Kafka Connector JAR (if not already included in your Flink distribution)
    # Updated Jar Config with JDBC and Postgres Driver

    # Kafka Connector: flink-sql-connector-kafka-3.1.0-1.18.jar - for reading from Kafka
    # JDBC Connector: flink-connector-jdbc-3.1.2-1.18.jar - for writing to Postgres. We need this to use the JDBC sink connector in our job. Written by the Flink community, this connector allows us to write results directly to a Postgres database using JDBC. Make sure to use a compatible version of the JDBC connector for your Flink version.
    # Postgres Driver: postgresql-42.7.2.jar - for Postgres connectivity. This is required by the JDBC connector to connect to Postgres. Make sure to use a compatible version of the Postgres driver for your Postgres version. Written by the PostgreSQL community, this driver allows Java applications (like Flink) to connect to a Postgres database using JDBC.
    logger.info("Adding required JARs for Kafka and JDBC connectors...")
    t_env.get_config().set(
        "pipeline.jars", 
        "file:///opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.19.jar;"
        "file:///opt/flink/lib/flink-connector-jdbc-3.2.0-1.19.jar;"
        "file:///opt/flink/lib/postgresql-42.7.5.jar"
    )

    # 2. Source DDL: Kafka/Redpanda
    logger.info("Creating source table for Kafka topic 'green-trips'...")
    t_env.execute_sql("""
        CREATE TABLE green_trips (
            PULocationID INT,
            tip_amount DOUBLE,
            lpep_pickup_datetime STRING,
            -- Convert string to Flink Timestamp
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            -- Define Watermark
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'properties.group.id' = 'q6-tumbling-group_2',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json',
            'json.ignore-parse-errors' = 'true'  -- Ignore malformed JSON records instead of failing the job
        )
    """)

    # 3. Sink DDL: PostgreSQL
    logger.info("Creating sink table in Postgres if it doesn't exist...")
    t_env.execute_sql("""
        CREATE TABLE tip_sink (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            total_tip_amount DOUBLE PRECISION
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/taxi_db',
            'table-name' = 'hourly_tip_totals',
            'username' = 'postgres',
            'password' = 'password',
            'driver' = 'org.postgresql.Driver'
        )
    """)

    # 4. Windowing Query and Job Submission with Job ID retrieval.
    logger.info("Submitting Flink job to process tumbling windows and write to Postgres...")
    table_result = t_env.execute_sql("""
        INSERT INTO tip_sink
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '1' HOUR) AS window_start,
            TUMBLE_END(event_timestamp, INTERVAL '1' HOUR) AS window_end,
            SUM(tip_amount) AS total_tip_amount
        FROM green_trips
        GROUP BY 
            TUMBLE(event_timestamp, INTERVAL '1' HOUR)
    """)
    
    # Immediately try to get the Job ID
    job_client = table_result.get_job_client()
    if job_client:
        logger.info(f"✅ Job submitted successfully! ID: {job_client.get_job_id()}")
    else:
        logger.warning("⚠️ Job submitted, but JobClient is not available yet.")

    # Only wait if you want the terminal to stay attached. It will block until the job finishes, which is not ideal for a streaming job. You can comment this out if you want to submit and detach immediately.
    #table_result.wait()
    logger.info("✅ Job submitted to cluster! Check http://localhost:8081")

if __name__ == '__main__':
    ensure_postgres_table()  # Ensure the Postgres table exists before running the job
    run_tumbling_window_job() # Start Flink job to process data and write to Postgres