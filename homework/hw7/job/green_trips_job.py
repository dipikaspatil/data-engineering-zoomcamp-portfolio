import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

def run_aggregation_job():
    # 1. Setup Environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1) # Crucial for 1-partition topic watermarks
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 2. Source DDL (Matches 8-column Producer)
    # Note: we use VARCHAR for the dates to convert them to TIMESTAMP locally
    source_ddl = """
        CREATE TABLE green_trips_source (
            lpep_pickup_datetime STRING,
            lpep_dropoff_datetime STRING,
            PULocationID INT,
            DOLocationID INT,
            passenger_count INT,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            total_amount DOUBLE,
            -- Create Flink Timestamp and Watermark
            event_time AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'properties.group.id' = 'flink-hw-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)

    # 3. Sink DDL (Postgres)
    sink_ddl = """
        CREATE TABLE trip_stats_sink (
            PULocationID INT,
            trip_count BIGINT,
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3)
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/taxi_db',
            'table-name' = 'trip_counts_window',
            'username' = 'postgres',
            'password' = 'password',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    # 4. Aggregation Query (5-minute windows)
    # This takes the 8 columns and shrinks them into 4 columns for the sink
    aggregation_query = """
        INSERT INTO trip_stats_sink
        SELECT 
            PULocationID, 
            COUNT(*) AS trip_count,
            TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
            TUMBLE_END(event_time, INTERVAL '5' MINUTE) AS window_end
        FROM green_trips_source
        GROUP BY 
            PULocationID, 
            TUMBLE(event_time, INTERVAL '5' MINUTE)
    """
    t_env.execute_sql(aggregation_query)

if __name__ == '__main__':
    run_aggregation_job()