# 01 - Docker + Postgres (docker-sql pipeline)

## 🧠 Overview

In this module, I set up a local **data ingestion pipeline** that uses **Docker** to run a PostgreSQL database and a Python ingestion script.  
The goal is to create a reproducible environment where raw CSV data can be imported into Postgres using containerized tools.

This serves as a foundation for more advanced data engineering workflows such as orchestration (Airflow), transformations, and analytics.

---

## 🛠 Tools & Technologies

| Category | Tool / Library |
|----------|----------------|
| Containerization | Docker, Docker Compose |
| Database | PostgreSQL |
| Language | Python |
| Data Processing | Pandas |
| Database Drivers | psycopg2, SQLAlchemy |
| Version Control | Git & GitHub |

---

## 📦 Architecture & Data Flow

Below is a simplified diagram showing how the ingestion pipeline works:

```text
CSV Dataset (NYC)
        │
        ▼
Python Ingestion Script
(Pandas + SQLAlchemy)
        │
        ▼
PostgreSQL (Docker Container)
```


**Data Flow Steps:**
1. Dataset is downloaded (from a public URL or local source).
2. Python script reads the CSV using Pandas.
3. Data is written into the Postgres database in chunks.
4. The Postgres database persists the data inside Docker.

---

## 📁 Components

### Docker
- `Dockerfile`: Builds the Python ingestion environment.
- PostgreSQL Docker image: Runs Postgres with environment variables for credentials and database.

### Python Script
- `ingest_data.py`: Reads a CSV file in chunks and writes to the Postgres database.
- Uses `Pandas` for data reading/processing.
- Uses `SQLAlchemy` and `psycopg2` for database connections.
- The ingestion script replaces the table if it exists on the first chunk and appends remaining chunks. This ensures the pipeline is idempotent and can be rerun without errors.”

### Docker Compose
- Combines multiple services (Python + Postgres).
- Ensures both services can communicate internally.
- Provides a single command to orchestrate the environment.

---

## 📌 How to Run (Local – draft)

> ⚠️ These are *starter steps*.  
> You can refine them once you’ve executed the pipeline yourself.

1️⃣ Start Docker containers
```bash
docker-compose up --build
```
Launch PostgreSQL and Python ingestion containers.

#### Expected Output / Screenshot:

```arduino
<Add terminal logs here or attach screenshot>
```

2️⃣ Check running containers
```bash
docker ps
```
Ensure both Postgres and Python containers are running.

#### Expected Output / Screenshot:

```css
<Container IDs, status, ports, etc.>
```

3️⃣ Connect to Postgres
```bash
psql -h localhost -U root -d ny_taxi
```
Or connect using pgAdmin/DBeaver with host localhost and port 5432.

#### Expected Output / Screenshot:

```sql
<Example psql prompt or pgAdmin table view>
```

4️⃣ Run Python ingestion script
```
docker exec -it <python-container-id> python ingest_data.py
```
Load CSV dataset into Postgres using Pandas + SQLAlchemy.

#### Expected Output / Screenshot:

```php-template
<Logs showing chunk processing or success message>
```

5️⃣ Verify data
```sql
SELECT COUNT(*) FROM taxi_data;
```
Confirm the data is loaded successfully.

#### Expected Output / Screenshot:

```sql
<Row count, sample rows, or pgAdmin screenshot>

```

6️⃣ Stop containers
```bash
docker compose down
```
Clean up all running containers.

#### Expected Output / Screenshot:
```php-template
<Docker stopped containers logs>
```

### Key Files

- `Dockerfile` – Builds Python container with dependencies for ingestion
- `docker-compose.yml` – Runs Postgres + Python containers, sets env variables
- `ingest_data.py` – Reads CSV in chunks using Pandas, writes to Postgres
- `requirements.txt` – Python libraries: pandas, sqlalchemy, psycopg2

🧠 Learnings / Notes

* Docker allows containerized, reproducible environments for Python and Postgres.

* Pandas chunked ingestion enables loading large datasets efficiently.

* SQLAlchemy + psycopg2 provide reliable DB connectivity inside containers.

* This setup forms a solid foundation for scheduling pipelines and data warehouse integration.

### Enhancements

- **Progress Monitoring with `tqdm`**  
  The ingestion script uses `tqdm` to display a progress bar for chunked CSV ingestion.  
  This provides visual feedback during long-running data loads, making the pipeline more user-friendly and professional.

### Optional: pgAdmin (PostgreSQL UI)

1 - pgAdmin is included as an optional service for inspecting the PostgreSQL database.
It can be used to verify table creation, schema, and ingested records.

Access: http://localhost:8080  
Default credentials:
- Email: admin@admin.com
- Password: admin

Postgres connection inside Docker:
- Host: postgres
- Port: 5432

2 - pgcli - to inspect the database from the terminal:

```bash
pgcli -h localhost -p 5432 -U root -d ny_taxi
```
 

🖼 Runtime Flow Diagram (Text-Based / ASCII for Markdown)

```text

docker-compose up --build
        │
        ▼
+---------------------------+
| Build ingest image        |
| (Dockerfile)              |
+---------------------------+
        │
        ▼
+---------------------------+
| Start Postgres container  |
| - Initializes DB          |
| - Listens on port 5432    |
+---------------------------+
        │
        ▼
+---------------------------+
| Start pgAdmin container   |
| - Web UI on port 8080     |
| - Connects to Postgres    |
| - Optional inspection     |
+---------------------------+
        │
        ▼
+---------------------------+
| Start Ingest container    |
| - Runs ingest_data.py     |
| - Reads CSV in chunks     |
| - Parses datetimes        |
| - Creates / appends table |
| - Progress bar via tqdm   |
+---------------------------+
        │
        ▼
+---------------------------+
| Ingest container exits    |
| - Data persisted in volume|
| - Postgres remains active |
+---------------------------+

```

### 🔹 Runtime Flow — Step-by-Step Explanation

#### 1. `docker-compose up --build`
- Triggers both **building and starting containers**.
- Ensures your **ingestion container is built from the Dockerfile** before running.

#### 2. Build ingest image (Dockerfile)
- Dockerfile creates a **Python environment** with:
  - Required libraries: `pandas`, `SQLAlchemy`, `tqdm`, `psycopg2`
  - Script: `ingest_data.py` copied inside
- Produces a **container image ready to run your ingestion**.

#### 3. Start Postgres container
- Initializes the database using environment variables:
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Creates a **persistent volume** (`pgdata`) for data storage.
- Listens on **port 5432** for connections.

#### 4. Start pgAdmin container (optional)
- Web-based GUI for inspecting Postgres.
- Connects to Postgres using **container name `postgres`** as host.
- Accessible at: [http://localhost:8080](http://localhost:8080)
- Useful for **schema verification and manual queries**.

#### 5. Start ingestion container
- Runs the script: `python ingest_data.py`.
- Execution flow inside the script:
  1. Reads environment variables (DB credentials, host)
  2. Downloads CSV dataset in **chunks**
  3. Parses **datetime columns explicitly**
  4. Loads the **first chunk** using `if_exists="replace"`
  5. Appends **remaining chunks** using `if_exists="append"`
  6. Displays progress with `tqdm`

#### 6. Ingestion container exits
- After all chunks are loaded, the container **stops automatically**.
- **Postgres continues running** with persisted data.
- Results can be inspected via **pgAdmin** or SQL queries.

