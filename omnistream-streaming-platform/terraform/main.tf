# 1. PROVIDER
provider "google" {
  project = var.project_id
  region  = var.region
}

# 2. STORAGE (GCS)

# 2.1. The GCS "Error Lake" for Dead Letter Queue
resource "google_storage_bucket" "error_lake" {
  name          = "${var.project_id}-error-lake"
  location      = var.region
  force_destroy = true
  storage_class = "STANDARD"
  uniform_bucket_level_access = true 
}

# 2.2. The GCS "Cold Archive" for Long-term Raw Storage
resource "google_storage_bucket" "cold_archive" {
  name          = "${var.project_id}-raw-archive"
  location      = var.region
  force_destroy = true # We definitely don't want to accidentally delete history
  storage_class = "COLDLINE"
  uniform_bucket_level_access = true

  # Optional: Move data to "Archive" class (cheapest) after 365 days
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }
}

# 3. ANALYTICS (BigQuery)

# 3.1 Staging Dataset with the 90-Day Purge (Where Flink Sinks)

resource "google_project_service" "bq_storage_api" {
  project = var.project_id
  service = "bigquerystorage.googleapis.com"
  disable_on_destroy = false
}

resource "google_bigquery_dataset" "staging_ds" {
  dataset_id                  = "omnistream_staging"
  friendly_name               = "Staging Data"
  description                 = "Real-time landing zone for Flink processed events"
  location                    = var.region
  delete_contents_on_destroy  = true
  
  # THE 90-DAY PURGE (in milliseconds)
  # 90 days * 24h * 60m * 60s * 1000ms
  default_partition_expiration_ms = 7776000000 
}

# 3.2 Gold Dataset (No expiration, this is our long-term analytical view) (Where dbt Sinks)
resource "google_bigquery_dataset" "gold_ds" {
  dataset_id                  = "omnistream_gold"
  friendly_name               = "Analytical Marts"
  description                 = "Clean, joined tables for Metabase Dashboards"
  location                    = var.region
  delete_contents_on_destroy  = true
}

# 3.3 Raw Aviation Table (Inside Staging)
resource "google_bigquery_table" "raw_aviation_data" {
  dataset_id = google_bigquery_dataset.staging_ds.dataset_id
  table_id   = "raw_aviation_data"

  # Recommended for development to allow 'terraform destroy' to work easily
  deletion_protection = false 

  # Partitioning by the time data arrives (helps BQ 90-day expiration logic)
  # By adding time_partitioning, BigQuery can efficiently drop data older than 90 days as defined in staging_ds
  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
[
  {"name": "record_key", "type": "STRING", "mode": "NULLABLE"},
  {"name": "icao24", "type": "STRING", "mode": "NULLABLE"},
  {"name": "callsign", "type": "STRING", "mode": "NULLABLE"},
  {"name": "origin_country", "type": "STRING", "mode": "NULLABLE"},
  {"name": "timestamp", "type": "INT64", "mode": "NULLABLE"},
  {"name": "latitude", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "longitude", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "velocity", "type": "FLOAT64", "mode": "NULLABLE"}
]
EOF
}

resource "google_bigquery_table" "raw_geo_data" {
  dataset_id = google_bigquery_dataset.staging_ds.dataset_id
  table_id   = "raw_geo_data"
  deletion_protection = false 

  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
[
  {"name": "record_key", "type": "STRING", "mode": "NULLABLE"},
  {"name": "id", "type": "STRING", "mode": "NULLABLE"},
  {"name": "mag", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "place", "type": "STRING", "mode": "NULLABLE"},
  {"name": "timestamp", "type": "INT64", "mode": "NULLABLE"},
  {"name": "lon", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "lat", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "depth", "type": "FLOAT64", "mode": "NULLABLE"}
]
EOF
}

resource "google_bigquery_table" "raw_finance_data" {
  dataset_id = google_bigquery_dataset.staging_ds.dataset_id
  table_id   = "raw_finance_data"
  deletion_protection = false 

  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
[
  {"name": "record_key", "type": "STRING", "mode": "NULLABLE"},
  {"name": "symbol", "type": "STRING", "mode": "NULLABLE"},
  {"name": "price", "type": "FLOAT64", "mode": "NULLABLE"},
  {"name": "volume", "type": "INT64", "mode": "NULLABLE"},
  {"name": "timestamp", "type": "INT64", "mode": "NULLABLE"},
  {"name": "change_percent", "type": "STRING", "mode": "NULLABLE"}
]
EOF
}

resource "google_bigquery_table" "dlq_control" {
  dataset_id = google_bigquery_dataset.staging_ds.dataset_id
  table_id   = "dlq_control"
  deletion_protection = false

  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
[
  {"name": "dlqId", "type": "STRING", "mode": "NULLABLE"},
  {"name": "sourceTopic", "type": "STRING", "mode": "NULLABLE"},
  {"name": "recordType", "type": "STRING", "mode": "NULLABLE"},
  {"name": "errorStage", "type": "STRING", "mode": "NULLABLE"},
  {"name": "errorType", "type": "STRING", "mode": "NULLABLE"},
  {"name": "errorClassification", "type": "STRING", "mode": "NULLABLE"},
  {"name": "status", "type": "STRING", "mode": "NULLABLE"},
  {"name": "retryCount", "type": "INT64", "mode": "NULLABLE"},
  {"name": "maxRetries", "type": "INT64", "mode": "NULLABLE"},
  {"name": "nextRetryAt", "type": "INT64", "mode": "NULLABLE"},
  {"name": "failedAt", "type": "INT64", "mode": "NULLABLE"},
  {"name": "lastRetriedAt", "type": "INT64", "mode": "NULLABLE"},
  {"name": "payloadGcsPath", "type": "STRING", "mode": "NULLABLE"},
  {"name": "idempotencyKey", "type": "STRING", "mode": "NULLABLE"},
  {"name": "failed_at_ts", "type": "TIMESTAMP", "mode": "NULLABLE"}
]
EOF
}

# 4. IDENTITY (IAM)

# 4.1 Service Account
resource "google_service_account" "omnistream_runner" {
  account_id   = "omnistream-runner"
  display_name = "OmniStream Pipeline Runner"
}

# 4.2 Permission to BigQuery Data Editor
resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.omnistream_runner.email}"
}

# 4.3 Permission to GCS Object Admin
resource "google_project_iam_member" "gcs_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.omnistream_runner.email}"
}

# 4.4 Permissions to include Archive access
resource "google_project_iam_member" "gcs_archive_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.omnistream_runner.email}"
}

# 4.5 Permission to run BigQuery Jobs
resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.omnistream_runner.email}"
}

# 4.6 Automatically generate a Service Account Key
resource "google_service_account_key" "omnistream_key" {
  service_account_id = google_service_account.omnistream_runner.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# 4.7 Save the key locally (No manual download needed)
resource "local_file" "service_account_key_file" {
  content  = base64decode(google_service_account_key.omnistream_key.private_key)
  filename = "${path.module}/../docker/key.json"
}

# 4.8 Explicit permission for BigQuery Storage API
resource "google_project_iam_member" "bq_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.omnistream_runner.email}"
}