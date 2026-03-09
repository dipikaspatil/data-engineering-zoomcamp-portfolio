## Module 6 Homework

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/06-batch/homework.md

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the Yellow 2025-11 data from the official website:

wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet

### Question 1: Install Spark and PySpark
- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.
    - What's the output?

#### Steps followed are as follows - 

#### 0. Setup Spark & PySpark

Install Spark locally (Mac example):

```bash
brew install apache-spark
```

Verify:

```bash
spark-shell
```

```scala
scala> spark.version
val res1: String = 4.1.1
```

or in Python:

```python
import pyspark
print(pyspark.__version__)
```

```bash
pyspark
```

Output - 
```
pyspark
Python 3.13.5 (main, Jun 11 2025, 15:36:57) [Clang 17.0.0 (clang-1700.0.13.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
WARNING: Using incubator modules: jdk.incubator.vector
Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
26/03/07 23:19:18 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 4.1.1
      /_/

Using Python version 3.13.5 (main, Jun 11 2025 15:36:57)
Spark context Web UI available at http://mac.attlocal.net:4040
Spark context available as 'sc' (master = local[*], app id = local-1772954358549).
SparkSession available as 'spark'.
>>>

>>> spark.version
'4.1.1'

```

#### Basic Local Spark Session (Recommended)

1. Create a Python script, e.g. spark_test.py.

    ```python
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("zoomcamp-test") \
        .getOrCreate()

    print(spark.version)
    ```

    Run it
    ```bash
    python spark_test.py
    ```

2. Using Jupyter Notebook

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("de-zoomcamp") \
    .getOrCreate()

spark
```

Output
```
SparkSession - in-memory

SparkContext

Spark UI

Version     v4.1.1
Master      local[*]
AppName     de-zoomcamp

```

`Answer - 4.1.1`

### Question 2: Yellow November 2025
Read the November 2025 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- 25MB
- 75MB
- 100MB

Steps followed - 

#### Step 1 — Download the November 2025 Yellow Taxi data parquet file

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
```

#### Verify the file exists

```python
import os

os.listdir(".")
```

Output 
```
['Untitled1.ipynb',
 'yellow_tripdata_2025-11.parquet',
 'Untitled.ipynb',
 'zoomcamp_env',
 'README.md',
 '.ipynb_checkpoints']
 ```

 #### Read file in spark

 ```python
 from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("YellowNovember") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.parquet("yellow_tripdata_2025-11.parquet")
df.show(5)
```

```output
+--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+------------------+
|VendorID|tpep_pickup_datetime|tpep_dropoff_datetime|passenger_count|trip_distance|RatecodeID|store_and_fwd_flag|PULocationID|DOLocationID|payment_type|fare_amount|extra|mta_tax|tip_amount|tolls_amount|improvement_surcharge|total_amount|congestion_surcharge|Airport_fee|cbd_congestion_fee|
+--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+------------------+
|       7| 2025-11-01 00:13:25|  2025-11-01 00:13:25|              1|         1.68|         1|                 N|          43|         186|           1|       14.9|  0.0|    0.5|       1.5|         0.0|                  1.0|       22.15|                 2.5|        0.0|              0.75|
|       2| 2025-11-01 00:49:07|  2025-11-01 01:01:22|              1|         2.28|         1|                 N|         142|         237|           1|       14.2|  1.0|    0.5|      4.99|         0.0|                  1.0|       24.94|                 2.5|        0.0|              0.75|
|       1| 2025-11-01 00:07:19|  2025-11-01 00:20:41|              0|          2.7|         1|                 N|         163|         238|           1|       15.6| 4.25|    0.5|      4.27|         0.0|                  1.0|       25.62|                 2.5|        0.0|              0.75|
|       2| 2025-11-01 00:00:00|  2025-11-01 01:01:03|              3|        12.87|         1|                 N|         138|         261|           1|       66.7|  6.0|    0.5|       0.0|        6.94|                  1.0|       86.14|                 2.5|       1.75|              0.75|
|       1| 2025-11-01 00:18:50|  2025-11-01 00:49:32|              0|          8.4|         1|                 N|         138|          37|           2|       39.4| 7.75|    0.5|       0.0|         0.0|                  1.0|       48.65|                 0.0|       1.75|               0.0|
+--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+------------------+
only showing top 5 rows
```

#### Repartition to 4 partitions and save as Parquet:

```python
df_repart = df.repartition(4)

df_repart.write.mode("overwrite").parquet("yellow_2025_11_repart")
```

#### Check the average size of the resulting Parquet files:

```bash
ls -lh yellow_2025_11_repart/
```

Output 

```
total 205312
-rw-r--r--  1 niteshmishra  staff     0B Mar  8 00:09 _SUCCESS
-rw-r--r--  1 niteshmishra  staff    24M Mar  8 00:09 part-00000-63162b34-b118-40ad-868e-55727140ced9-c000.snappy.parquet
-rw-r--r--  1 niteshmishra  staff    24M Mar  8 00:09 part-00001-63162b34-b118-40ad-868e-55727140ced9-c000.snappy.parquet
-rw-r--r--  1 niteshmishra  staff    24M Mar  8 00:09 part-00002-63162b34-b118-40ad-868e-55727140ced9-c000.snappy.parquet
-rw-r--r--  1 niteshmishra  staff    24M Mar  8 00:09 part-00003-63162b34-b118-40ad-868e-55727140ced9-c000.snappy.parquet
```

Answer - ~25 MB

### Question 3: Count records
How many taxi trips were there on the 15th of November?

Consider only trips that started on the 15th of November.

- 62,610
- 102,340
- 162,604
- 225,768

#### Steps followed are as follows - 

- Check DataFrame schema

```python
df.printSchema()
```

```output
root
 |-- VendorID: integer (nullable = true)
 |-- tpep_pickup_datetime: timestamp_ntz (nullable = true)
 |-- tpep_dropoff_datetime: timestamp_ntz (nullable = true)
 |-- passenger_count: long (nullable = true)
 |-- trip_distance: double (nullable = true)
 |-- RatecodeID: long (nullable = true)
 |-- store_and_fwd_flag: string (nullable = true)
 |-- PULocationID: integer (nullable = true)
 |-- DOLocationID: integer (nullable = true)
 |-- payment_type: long (nullable = true)
 |-- fare_amount: double (nullable = true)
 |-- extra: double (nullable = true)
 |-- mta_tax: double (nullable = true)
 |-- tip_amount: double (nullable = true)
 |-- tolls_amount: double (nullable = true)
 |-- improvement_surcharge: double (nullable = true)
 |-- total_amount: double (nullable = true)
 |-- congestion_surcharge: double (nullable = true)
 |-- Airport_fee: double (nullable = true)
 |-- cbd_congestion_fee: double (nullable = true)
 ```

pickup datetime column, usually called: tpep_pickup_datetime (Yellow taxi data)

It is `timestamp`.

- Filter trips on the 15th of November

    - If it’s a timestamp:
    ```python
    from pyspark.sql.functions import to_date

    df_15 = df.filter(
        (col("tpep_pickup_datetime") >= "2025-11-15 00:00:00") &
        (col("tpep_pickup_datetime") <  "2025-11-16 00:00:00")  
    )
    ```

- Count the records

```python
count_15 = df_15.count()
print(count_15)
```

```output
162604
```

Answer - `162604`

### Question 4: Longest trip
What is the length of the longest trip in the dataset in hours?

22.7
58.2
90.6
134.5

```python
from pyspark.sql import functions as F

df_with_trip_duration = df.withColumn("trip_duration_hours", 
                                      (F.unix_timestamp(F.col("tpep_dropoff_datetime")) - F.unix_timestamp(F.col("tpep_pickup_datetime")))/3600
                                     )
df_agg = df_with_trip_duration.agg(F.max("trip_duration_hours"))
df_agg.show()
```

Output - 

```
+------------------------+
|max(trip_duration_hours)|
+------------------------+
|       90.64666666666666|
+------------------------+
```

Answer - `90.6`

### Question 5: User Interface
Spark's User Interface which shows the application's dashboard runs on which local port?

80
443
4040
8080

```
Spark’s UI / Web UI / Spark Dashboard runs locally by default on port 4040.

This dashboard shows:

Jobs, stages, and tasks

Executors and memory usage

Storage and environment info
```

Notes:

- If port 4040 is already in use, Spark will try 4041, 4042, … until it finds a free port.

- We can always see the active port in the terminal when we start a SparkSession:

```logs
26/03/08 00:06:36 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.
```

Answer - default `4040`

### Question 6: Least frequent pickup location zone
Load the zone lookup data into a temp view in Spark:

wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

- Governor's Island/Ellis Island/Liberty Island
- Arden Heights
- Rikers Island
- Jamaica Bay
If multiple answers are correct, select any

#### Steps followed as follows - 

- Step 1 — Download the zone lookup file

    ```python
    !wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
    ```

- Step 2 — Read it into Spark

    ```python
    zones = spark.read
        .option("header", "true")
        .csv("taxi_zone_lookup.csv")
    ```

- Step 3 — Join with taxi dataset

    ```python
    df_joined = df.join(
                    zones,
                    df.PULocationID == zones.LocationID,
                    "left"
                )
    ```

- Step 4 — Count trips per pickup zone

    ```python
    from pyspark.sql import functions as F

    # This sorts zones from least frequent → most frequent.
    zone_counts = (
        df_joined
        .groupBy("Zone")
        .agg(F.count("*").alias("trip_count"))
        .orderBy("trip_count")
    )

    zone_counts.show(10)
    ```

Output - 
```
--2026-03-08 18:40:53--  https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
Resolving d37ci6vzurychx.cloudfront.net (d37ci6vzurychx.cloudfront.net)... 2600:9000:234c:3800:b:20a5:b140:21, 2600:9000:234c:e600:b:20a5:b140:21, 2600:9000:234c:5400:b:20a5:b140:21, ...
Connecting to d37ci6vzurychx.cloudfront.net (d37ci6vzurychx.cloudfront.net)|2600:9000:234c:3800:b:20a5:b140:21|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 12331 (12K) [text/csv]
Saving to: ‘taxi_zone_lookup.csv.3’

taxi_zone_lookup.cs 100%[===================>]  12.04K  --.-KB/s    in 0.001s  

2026-03-08 18:40:53 (11.4 MB/s) - ‘taxi_zone_lookup.csv.3’ saved [12331/12331]

+---------------------------------------------+----------+
|Zone                                         |trip_count|
+---------------------------------------------+----------+
|Governor's Island/Ellis Island/Liberty Island|1         |
|Eltingville/Annadale/Prince's Bay            |1         |
|Arden Heights                                |1         |
|Port Richmond                                |3         |
|Rikers Island                                |4         |
|Rossville/Woodrow                            |4         |
|Great Kills                                  |4         |
|Green-Wood Cemetery                          |4         |
|Jamaica Bay                                  |5         |
|Westerleigh                                  |12        |
+---------------------------------------------+----------+
only showing top 10 rows
```

Answer - `Governor's Island/Ellis Island/Liberty Island`

