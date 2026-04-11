# 1. The Service Account Email (You'll need this for IAM checks)
output "service_account_email" {
  description = "The email of the OmniStream runner service account"
  value       = google_service_account.omnistream_runner.email
}

# 2. GCS Bucket Names (You'll need these for your Python/Flink sinks)
output "error_lake_bucket" {
  value = google_storage_bucket.error_lake.name
}

output "cold_archive_bucket" {
  value = google_storage_bucket.cold_archive.name
}

# 3. BigQuery Dataset IDs (You'll need these for dbt and Flink)
output "staging_dataset_id" {
  value = google_bigquery_dataset.staging_ds.dataset_id
}

output "gold_dataset_id" {
  value = google_bigquery_dataset.gold_ds.dataset_id
}