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

2️⃣ Check running containers
```bash
docker ps
```
Ensure both Postgres and Python containers are running.

3️⃣ Connect to Postgres
```bash
psql -h localhost -U root -d ny_taxi
```
Or connect using pgAdmin/DBeaver with host localhost and port 5432.

4️⃣ Run Python ingestion script
```
docker exec -it <python-container-id> python ingest_data.py
```
Load CSV dataset into Postgres using Pandas + SQLAlchemy.

5️⃣ Verify data
```sql
SELECT COUNT(*) FROM taxi_data;
```
Confirm the data is loaded successfully.

6️⃣ Stop containers
```bash
docker compose down
```
Clean up all running containers.

### Key Files

- `Dockerfile` – Builds Python container with dependencies for ingestion
- `docker-compose.yml` – Runs Postgres + Python containers, sets env variables
- `ingest_data.py` – Reads CSV in chunks using Pandas, writes to Postgres
- `requirements.txt` – Python libraries: pandas, sqlalchemy, psycopg2

