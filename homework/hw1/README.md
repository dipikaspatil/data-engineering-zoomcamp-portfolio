# Homework 1 – Data Engineering Zoomcamp

This homework demonstrates a complete **local data ingestion pipeline** using **Docker, Docker Compose, PostgreSQL, pgAdmin, and Python (pandas + SQLAlchemy)**. The goal is to ingest NYC Green Taxi trip data and Taxi Zone lookup data into Postgres and answer analytical questions using SQL.

---

## 📁 Project Structure

```
hw1/
├── data/
│   ├── green_tripdata_2025-11.parquet
│   └── taxi_zone_lookup.csv
├── scripts/
│   └── ingest_data_hw1.py
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧱 Tech Stack

* **Python 3.10**
* **pandas** – data processing
* **SQLAlchemy** – database connection
* **PostgreSQL 15** – data warehouse
* **pgAdmin 4** – database UI
* **Docker & Docker Compose** – containerization

---

## 🐳 Docker Setup

### Services

* **postgres** – PostgreSQL database
* **pgadmin** – Web UI for Postgres
* **ingest** – One-time container to load data

### Named Volume

```yaml
volumes:
  pgdata:
```

* Persists Postgres data across container restarts
* Data is **deleted only** when running `docker-compose down -v`

---

## 🐍 Data Ingestion Logic

### Green Taxi Trips

* Source: `green_tripdata_2025-11.parquet`
* Loaded using `pandas.read_parquet`
* Written to Postgres in **chunks of 100,000 rows**
* Table name: **`green_ny_taxi_data`**

### Taxi Zones

* Source: `taxi_zone_lookup.csv`
* Loaded using `pandas.read_csv`
* Table name: **`zones`**

The ingestion container exits automatically after completing the load.

---

## ▶️ How to Run

From the `hw1` directory:

```bash
docker-compose up --build
```

This will:

1. Build the ingestion image
2. Start Postgres and pgAdmin
3. Load taxi data into Postgres
4. Exit the ingestion container

Access pgAdmin at:

```
http://localhost:8080
```

Login credentials:

* Email: `admin@admin.com`
* Password: `admin`

---

## 🧹 Cleanup

### Stop containers (keep data)

```bash
docker-compose down
```

### Stop containers **and delete database data**

```bash
docker-compose down -v
```

### Clean unused Docker resources (used when build errors occurred)

```bash
docker system prune -a
```

---

## 🧠 Key Learnings

* Difference between **containers vs volumes**
* Why ingestion containers exit while databases keep running
* Postgres **column names are case-sensitive** when quoted
* Docker volumes persist data even after container restarts
* How `docker-compose down -v` removes persistent state

---

## 📊 Homework SQL Questions

All analytical questions were answered using SQL queries executed via pgAdmin against the ingested data.

- Question 1 
    
    What's the version of pip in the python:3.13 image? (1 point)

    Steps - 

    ```bash
    docker run --rm -it python:3.13 bash
    pip --version
    ```

    Output -

    ```bash
    pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
    ```

    ✅ Answer: pip 25.3

- Question 2 

    Given the docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database? (1 point)

    ✅ Answer: postgres:5432
    Hostname: postgres
    Port: 5432

- Question 3

    For the trips in November 2025, how many trips had a trip_distance of less than or equal to 1 mile? (1 point)

    SQL Query:

    ```sql
    SELECT count(*)
    FROM green_ny_taxi_data
    WHERE trip_distance <= 1 
    AND lpep_pickup_datetime >= '2025-11-01'
    AND lpep_pickup_datetime < '2025-12-01'
    ```

    ✅ Answer: 8007

- Question 4

    Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles. (1 point)

    SQL Query - 

    ```sql
    SELECT 
        DATE(lpep_pickup_datetime) AS pickup_day,
        MAX(trip_distance) AS max_trip_distance
    FROM green_ny_taxi_data
    WHERE trip_distance < 100
    GROUP BY pickup_day
    ORDER BY max_trip_distance DESC
    LIMIT 1;

    OR 

    SELECT
        max(g.trip_distance) AS max_trip_distance,
        DATE(g.lpep_pickup_datetime) AS pickup_day
    FROM (
    SELECT * FROM green_ny_taxi_data
    WHERE trip_distance < 100
    ) AS g
    GROUP BY pickup_day
    ORDER BY max_trip_distance DESC
    LIMIT 1;
    ```

    ✅ Answer: 2025-11-14

    Query Output - 
    ```text
    "pickup_day"	"max_trip_distance"
    "2025-11-14"	88.03
    ```

- Question 5

    Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025? (1 point)

    SQL Query - 

    ```sql
    SELECT "Zone"
    FROM zones
    WHERE "LocationID" = (SELECT taxi_data.pickup_zone_id
                FROM (SELECT 
                    SUM(total_amount) as sum_total_amount,
                    "PULocationID" AS pickup_zone_id
                FROM green_ny_taxi_data
                WHERE DATE(lpep_pickup_datetime) = '2025-11-18'
                GROUP BY pickup_zone_id
                ORDER BY sum_total_amount DESC
                LIMIT 1) AS taxi_data)
    ```

    ✅ Answer: East Harlem North

- Question 6

    For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip? (1 point)

    SQL Query -

    ```sql
    SELECT t.tip_amount as tip_amount,
	   pickup_zones."Zone" AS pickup_zone,
	   dropoff_zones."Zone" AS dropoff_zone
    FROM green_ny_taxi_data t
    LEFT JOIN zones pickup_zones
    ON t."PULocationID" = pickup_zones."LocationID"
    LEFT JOIN zones dropoff_zones
    ON t."DOLocationID" = dropoff_zones."LocationID"
    WHERE pickup_zones."Zone" = 'East Harlem North'
    AND lpep_pickup_datetime >= '2025-11-01'
    AND lpep_pickup_datetime < '2025-12-01'
    ORDER BY tip_amount DESC
    LIMIT 1
    ```

    ✅ Answer: Yorkville West

    Query Output - 
    ```text
    "tip_amount"	"pickup_zone"	        "dropoff_zone"
    81.89	        "East Harlem North"	    "Yorkville West"
    ```

- Question 7

    Which of the following sequences describes the Terraform workflow for: 1) Downloading plugins and setting up backend, 2) Generating and executing changes, 3) Removing all resources? (1 point)

    ✅ Answer: terraform init, terraform apply -auto-approve, terraform destroy

---

## ✅ Status

✔️ Data ingested successfully
✔️ Queries validated in pgAdmin
✔️ Homework completed

---

## ⚠️ Troubleshooting Docker Build Errors

#### 1 - After stopping and rerunning `docker-compose up --build`, if you encounter errors like:

```pgsql
failed to prepare extraction snapshot … parent snapshot … does not exist
```
It usually means Docker’s local cache/layers got corrupted. The fix:

```
# Remove unused containers, images, volumes, and caches
docker system prune -a --volumes

# Rebuild the project
docker-compose up --build
```

-a → removes all unused images, not just dangling ones

--volumes → removes unused volumes

After pruning, rebuild of Docker image forces Docker to start fresh, so the snapshot/layer issue should be gone.


💡 Tip: This cleans up old images and volumes, so your builds start fresh. Make sure you don’t have other important containers/images before running.

#### 2 - I made a typo in table creation - gree_ny_taxi_data, so I stopped and rerant with correct table name - green_ny_taxi_data. But it did not clear my old table from database - gree_ny_taxi_data

Even if you “stop” or “remove” a container, the data in Postgres is stored in a named volume, which survives container restarts.

In my docker-compose.yml I have:

```yaml
volumes:
  pgdata:
  ```

And in the postgres service:

```yaml
volumes:
  - pgdata:/var/lib/postgresql/data
```

✅ This means: pgdata keeps the database files even if you remove the container.

So when I restart or rebuild the container, Postgres sees the old database already there and does not re-initialize it. That’s why the old table gree_ny_taxi_data still exists.

Remove the volume entirely

```bash
docker-compose down -v
```

The -v flag deletes all named volumes (like pgdata), so Postgres starts fresh.

Warning: All previous tables/data will be gone.
