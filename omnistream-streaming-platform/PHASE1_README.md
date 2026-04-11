# Phase 1 Implementation 

🟢 Phase 1: The Foundation (Infrastructure-as-Code)
Before writing a single line of Python or Java, the "vessels" must exist.

- Step 1: Terraform Setup. Create the GCS "Error Lake," the BigQuery staging and gold datasets, and the service accounts with correct permissions. Also create GCS "Cold Archive"

- Step 2: Docker Orchestration. set up your docker-compose.yaml with Redpanda (easier than Kafka for dev), Flink JobManager/TaskManager, and Airflow.

Goal: I should be able to run docker-compose up and see all your "servers" waiting for data.

------------------------------------------------------------------------------------------------------------

## 🛠️ Step 1: Terraform Setup (The Cloud Vessels)

#### terraform/: The Infrastructure-as-Code (IaC) layer.

- main.tf: The primary configuration file containing all cloud resources (GCS buckets, BigQuery datasets, and IAM roles).

- variables.tf: Defines the input variables (like Project ID and Region) required by the Terraform configuration.

- dev.tfvars: A configuration-specific file used to store actual values for the development environment.

- outputs.tf: Defines the "success receipt" that prints out resource names and IDs for use in other parts of the pipeline.

### Two Small "Pre-Flight" Checks:
Before we run terraform apply, make sure these two things are true in your GCP Console:

- Billing is enabled: Even though we are using the Free Tier/Trial, GCP requires a billing account linked to the project to create BigQuery datasets and GCS buckets.

- APIs are enabled: Terraform will try to talk to BigQuery and GCS. It's best to enable these APIs manually once, or Terraform might throw an error saying "API not enabled."

Search for "BigQuery API" and "Google Cloud Storage JSON API" in the GCP search bar and click Enable.

### Execute
```bash

terraform init

# Output

...
Terraform has been successfully initialized!
...
```

```bash
# Dry run
terraform plan -var-file="dev.tfvars"

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # google_bigquery_dataset.gold_ds will be created
  + resource "google_bigquery_dataset" "gold_ds" {
      + creation_time              = (known after apply)
      + dataset_id                 = "omnistream_gold"
      + default_collation          = (known after apply)
      + delete_contents_on_destroy = false
      + description                = "Clean, joined tables for Metabase Dashboards"
      + effective_labels           = {
          + "goog-terraform-provisioned" = "true"
        }
      + etag                       = (known after apply)
      + friendly_name              = "Analytical Marts"
      + id                         = (known after apply)
      + is_case_insensitive        = (known after apply)
      + last_modified_time         = (known after apply)
      + location                   = "us-central1"
      + max_time_travel_hours      = (known after apply)
      + project                    = "de-zoomcamp-2026-486900"
      + self_link                  = (known after apply)
      + storage_billing_model      = (known after apply)
      + terraform_labels           = {
          + "goog-terraform-provisioned" = "true"
        }

      + access (known after apply)
    }

  # google_bigquery_dataset.staging_ds will be created
  + resource "google_bigquery_dataset" "staging_ds" {
      + creation_time                   = (known after apply)
      + dataset_id                      = "omnistream_staging"
      + default_collation               = (known after apply)
      + default_partition_expiration_ms = 7776000000
      + delete_contents_on_destroy      = false
      + description                     = "Real-time landing zone for Flink processed events"
      + effective_labels                = {
          + "goog-terraform-provisioned" = "true"
        }
      + etag                            = (known after apply)
      + friendly_name                   = "Staging Data"
      + id                              = (known after apply)
      + is_case_insensitive             = (known after apply)
      + last_modified_time              = (known after apply)
      + location                        = "us-central1"
      + max_time_travel_hours           = (known after apply)
      + project                         = "de-zoomcamp-2026-486900"
      + self_link                       = (known after apply)
      + storage_billing_model           = (known after apply)
      + terraform_labels                = {
          + "goog-terraform-provisioned" = "true"
        }

      + access (known after apply)
    }

  # google_project_iam_member.bq_editor will be created
  + resource "google_project_iam_member" "bq_editor" {
      + etag    = (known after apply)
      + id      = (known after apply)
      + member  = "serviceAccount:omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + project = "de-zoomcamp-2026-486900"
      + role    = "roles/bigquery.dataEditor"
    }

  # google_project_iam_member.bq_job_user will be created
  + resource "google_project_iam_member" "bq_job_user" {
      + etag    = (known after apply)
      + id      = (known after apply)
      + member  = "serviceAccount:omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + project = "de-zoomcamp-2026-486900"
      + role    = "roles/bigquery.jobUser"
    }

  # google_project_iam_member.gcs_admin will be created
  + resource "google_project_iam_member" "gcs_admin" {
      + etag    = (known after apply)
      + id      = (known after apply)
      + member  = "serviceAccount:omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + project = "de-zoomcamp-2026-486900"
      + role    = "roles/storage.objectAdmin"
    }

  # google_project_iam_member.gcs_archive_admin will be created
  + resource "google_project_iam_member" "gcs_archive_admin" {
      + etag    = (known after apply)
      + id      = (known after apply)
      + member  = "serviceAccount:omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + project = "de-zoomcamp-2026-486900"
      + role    = "roles/storage.objectAdmin"
    }

  # google_service_account.omnistream_runner will be created
  + resource "google_service_account" "omnistream_runner" {
      + account_id   = "omnistream-runner"
      + disabled     = false
      + display_name = "OmniStream Pipeline Runner"
      + email        = "omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + id           = (known after apply)
      + member       = "serviceAccount:omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
      + name         = (known after apply)
      + project      = "de-zoomcamp-2026-486900"
      + unique_id    = (known after apply)
    }

  # google_service_account_key.omnistream_key will be created
  + resource "google_service_account_key" "omnistream_key" {
      + id                 = (known after apply)
      + key_algorithm      = "KEY_ALG_RSA_2048"
      + name               = (known after apply)
      + private_key        = (sensitive value)
      + private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
      + public_key         = (known after apply)
      + public_key_type    = "TYPE_X509_PEM_FILE"
      + service_account_id = (known after apply)
      + valid_after        = (known after apply)
      + valid_before       = (known after apply)
    }

  # google_storage_bucket.cold_archive will be created
  + resource "google_storage_bucket" "cold_archive" {
      + effective_labels            = {
          + "goog-terraform-provisioned" = "true"
        }
      + force_destroy               = false
      + id                          = (known after apply)
      + location                    = "US-CENTRAL1"
      + name                        = "de-zoomcamp-2026-486900-raw-archive"
      + project                     = (known after apply)
      + project_number              = (known after apply)
      + public_access_prevention    = (known after apply)
      + rpo                         = (known after apply)
      + self_link                   = (known after apply)
      + storage_class               = "COLDLINE"
      + terraform_labels            = {
          + "goog-terraform-provisioned" = "true"
        }
      + time_created                = (known after apply)
      + uniform_bucket_level_access = (known after apply)
      + updated                     = (known after apply)
      + url                         = (known after apply)

      + lifecycle_rule {
          + action {
              + storage_class = "ARCHIVE"
              + type          = "SetStorageClass"
            }
          + condition {
              + age                    = 365
              + matches_prefix         = []
              + matches_storage_class  = []
              + matches_suffix         = []
              + with_state             = (known after apply)
                # (3 unchanged attributes hidden)
            }
        }

      + soft_delete_policy (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # google_storage_bucket.error_lake will be created
  + resource "google_storage_bucket" "error_lake" {
      + effective_labels            = {
          + "goog-terraform-provisioned" = "true"
        }
      + force_destroy               = true
      + id                          = (known after apply)
      + location                    = "US-CENTRAL1"
      + name                        = "de-zoomcamp-2026-486900-error-lake"
      + project                     = (known after apply)
      + project_number              = (known after apply)
      + public_access_prevention    = (known after apply)
      + rpo                         = (known after apply)
      + self_link                   = (known after apply)
      + storage_class               = "STANDARD"
      + terraform_labels            = {
          + "goog-terraform-provisioned" = "true"
        }
      + time_created                = (known after apply)
      + uniform_bucket_level_access = (known after apply)
      + updated                     = (known after apply)
      + url                         = (known after apply)

      + soft_delete_policy (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # local_file.service_account_key_file will be created
  + resource "local_file" "service_account_key_file" {
      + content              = (sensitive value)
      + content_base64sha256 = (known after apply)
      + content_base64sha512 = (known after apply)
      + content_md5          = (known after apply)
      + content_sha1         = (known after apply)
      + content_sha256       = (known after apply)
      + content_sha512       = (known after apply)
      + directory_permission = "0777"
      + file_permission      = "0777"
      + filename             = "./omnistream-key.json"
      + id                   = (known after apply)
    }

Plan: 11 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + cold_archive_bucket   = "de-zoomcamp-2026-486900-raw-archive"
  + error_lake_bucket     = "de-zoomcamp-2026-486900-error-lake"
  + gold_dataset_id       = "omnistream_gold"
  + service_account_email = "omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
  + staging_dataset_id    = "omnistream_staging"

───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.
```

Everything looks exactly as it should:

- Storage: Buckets have the correct storage classes (STANDARD for errors, COLDLINE for archives).

- Analytics: BigQuery datasets are ready with the correct 90-day expiration for staging.

- Security: Service Account is mapped to the correct roles, and most importantly, local_file.service_account_key_file is ready to drop that .json key right into local folder.

```bash
terraform apply -var-file="dev.tfvars"
```

| Item | Status | Purpose |
|------|--------|---------|
| omnistream-key.json | ✅ In your folder | Local Docker containers use this to authenticate and communicate with GCP |
| GCS Buckets | ✅ Live in GCP | Stores raw logs and error data |
| BigQuery Datasets | ✅ Live in GCP | Holds staging and gold layers for SQL analysis |
| Service Account | ✅ Live in GCP | Acts as the identity with permissions to move data across services |

Check Output

```bash

terraform output

# Output
cold_archive_bucket = "de-zoomcamp-2026-486900-raw-archive"
error_lake_bucket = "de-zoomcamp-2026-486900-error-lake"
gold_dataset_id = "omnistream_gold"
service_account_email = "omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
staging_dataset_id = "omnistream_staging"
```

### Troubleshoot

`Problem` - zsh: command not found: terraform

```bash
08-capstone % terraform init
zsh: command not found: terraform
```

`Solution` - 🛠️ 1. Install Terraform

Run this command in your terminal:

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

Verify
```bash
terraform -version

# Output
Terraform v1.14.7
on darwin_arm64
```

`Problem` - Error while exeuting plan -  `error: google: could not find default credentials.`

```bash
terraform plan -var-file="dev.tfvars"

Planning failed. Terraform encountered an error while generating this plan.

╷
│ Error: Attempted to load application default credentials since neither `credentials` nor `access_token` was set in the provider block.  No credentials loaded. To use your gcloud credentials, run 'gcloud auth application-default login'.  Original error: google: could not find default credentials. See https://cloud.google.com/docs/authentication/external/set-up-adc for more information
│
│   with provider["registry.terraform.io/hashicorp/google"],
│   on main.tf line 2, in provider "google":
│    2: provider "google" {
```

- It basically means Terraform is knocking on Google Cloud's door, but Google doesn't know who is asking because there’s no "ID card" (credentials) presented.

- We have to use Application Default Credentials (ADC). This lets Terraform "borrow" your identity from the Google Cloud CLI.

`Solution` -
🛠️ The Fix (Run these in your terminal)
Log in to the Google Cloud CLI:
Run this command. It will open a tab in your web browser.

```bash
gcloud auth application-default login
```
- Select your Google account.
- Click Allow.
- Go back to your terminal; you should see a "Credentials saved" message.

Verify the Handshake:
Run the plan again:

```bash
terraform plan -var-file="dev.tfvars"
```

🔍 Why did this happen?
When I wrote provider "google" {} in your main.tf, I didn't hardcode a path to a key file. Terraform then looks for a "Standard" place on Mac where Google stores login tokens. If I haven't run the login command above, that folder is empty, and Terraform hits a wall.

🚦 What if gcloud is missing?
If terminal says `zsh: command not found: gcloud`, we need to install the Google Cloud SDK first:

```bash
curl https://sdk.cloud.google.com | bash
```
During the installation, it will ask you a few questions:

- Installation directory (this will create a google-cloud-sdk subdirectory) (/Users/niteshmishra): Hit Enter ans choose default

- Xcode Command Line Tools is already installed. Password: Mac password

- "Help improve the Google Cloud CLI?" (y/n) — Your choice.

- "Modify profile to update your $PATH?" — SAY YES. This fixes the "command not found" issue permanently.

- "Enter a path to an rc file to update" — Just hit Enter to accept the default (usually ~/.zshrc).

Then close terminal. 

Verify
```bash
gcloud --version

# Output - 
Google Cloud SDK 561.0.0
bq 2.1.29
core 2026.03.13
gcloud-crc32c 1.0.0
gsutil 5.36
```

Then run the gcloud auth... command.

#### docker/: Contains the orchestration logic to run the platform locally.

docker-compose.yaml: Coordinates the local "servers" (Redpanda, Flink, Airflow, and Postgres).
    
`Problem` - Error during terraform apply command

```bash
terraform apply -var-file="dev.tfvars"

local_file.service_account_key_file: Creation complete after 0s [id=edcab3d3a70459341037a4c2b81fd527456ae122]
╷
│ Error: googleapi: Error 412: Request violates constraint 'constraints/storage.uniformBucketLevelAccess', conditionNotMet
│
│   with google_storage_bucket.error_lake,
│   on main.tf line 10, in resource "google_storage_bucket" "error_lake":
│   10: resource "google_storage_bucket" "error_lake" {
│
╵
╷
│ Error: googleapi: Error 412: Request violates constraint 'constraints/storage.uniformBucketLevelAccess', conditionNotMet
│
│   with google_storage_bucket.cold_archive,
│   on main.tf line 18, in resource "google_storage_bucket" "cold_archive":
│   18: resource "google_storage_bucket" "cold_archive" {
│
```

This is a classic "Organizational Policy" error. Many modern Google Cloud projects have a security rule enforced at the top level that mandates all storage buckets use Uniform Bucket-Level Access.

Terraform tried to create the buckets with the old "legacy" settings, and Google Cloud's security guard blocked the door.

`Solution`
🛠️ The Fix: Update main.tf

I need to explicitly tell Terraform to follow this security rule. Add uniform_bucket_level_access = true to both of the bucket resources in main.tf.

Updated code will look like this:

```Terraform
resource "google_storage_bucket" "error_lake" {
  name          = "${var.project_id}-error-lake"
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = true
  
  # Add this line:
  uniform_bucket_level_access = true 
}

resource "google_storage_bucket" "cold_archive" {
  name          = "${var.project_id}-raw-archive"
  location      = var.region
  storage_class = "COLDLINE"

  # Add this line:
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
    condition {
      age = 365
    }
  }
}
```

## 📦 Step 2: Docker Orchestration Preview
Once we run terraform apply, we will have our cloud destination. Next, we prepare the local environment. Our docker-compose.yaml is the "orchestra conductor."

The Services we are about to link:

- Redpanda: Our ultra-fast message bus (Kafka compatible).

- Redpanda Console: A web UI so we can actually see the messages flying by.

- Flink JobManager: The brain of the stream processing.

- Flink TaskManager: The muscle that does the work.

- Airflow (Webserver/Scheduler): The maintenance and retry logic.

- Postgres - To store metadata

#### Port Map Summary
Once you run docker compose up -d, your "Command Center" will be spread across these three tabs in your browser:

Airflow: http://localhost:8080 (The Batch/dbt Scheduler)

Flink: http://localhost:8081 (The Real-time Engine)

Redpanda Console: http://localhost:8082 (The Stream Inspector)

### Run 
```bash
cd docker
docker compose build

# Output
[+] Building 1.8s (14/14) FINISHED
 => [internal] load local bake definitions                                                                                                                                     0.0s
 => => reading from stdin 856B                                                                                                                                                 0.0s
 => [taskmanager internal] load build definition from Dockerfile                                                                                                               0.0s
 => => transferring dockerfile: 1.49kB                                                                                                                                         0.0s
 => [taskmanager internal] load metadata for docker.io/library/flink:1.19.0-scala_2.12                                                                                         0.9s
 => [taskmanager internal] load .dockerignore                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                0.0s
 => [taskmanager 1/6] FROM docker.io/library/flink:1.19.0-scala_2.12@sha256:61355051b493c0b2784ae5755608798e7c54d9db0f8467e9e3f183e3a48e617a                                   0.0s
 => => resolve docker.io/library/flink:1.19.0-scala_2.12@sha256:61355051b493c0b2784ae5755608798e7c54d9db0f8467e9e3f183e3a48e617a                                               0.0s
 => CACHED [taskmanager 2/6] RUN apt-get update -y &&     apt-get install -y python3 python3-pip python3-dev openjdk-11-jdk-headless &&     rm -rf /var/lib/apt/lists/*        0.0s
 => CACHED [taskmanager 3/6] RUN ln -s /usr/bin/python3 /usr/bin/python                                                                                                        0.0s
 => CACHED [taskmanager 4/6] RUN mkdir -p /opt/java &&     ln -s /usr/lib/jvm/java-11-openjdk-arm64 /opt/java/openjdk                                                          0.0s
 => CACHED [taskmanager 5/6] RUN pip3 install --no-cache-dir     apache-flink==1.19.0     psycopg2-binary                                                                      0.0s
 => CACHED [taskmanager 6/6] RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.19/flink-sql-connector-kafka  0.0s
 => [taskmanager] exporting to image                                                                                                                                           0.1s
 => => exporting layers                                                                                                                                                        0.0s
 => => exporting manifest sha256:a907c780d76d21d74fb34128850284cb3b7c95fbdc4cfd97aa6929f6c87bfce9                                                                              0.0s
 => => exporting config sha256:e6c82652b45617a085003dee1de0d6dd0f79a6e158958c111f8c7f3d8702df44                                                                                0.0s
 => => exporting attestation manifest sha256:2b10d3b8e076d577f4fee9ef58db141104acad06cecf0491f1adfbde29e70371                                                                  0.0s
 => => exporting manifest list sha256:c94948813cfdb9f708dc1c7317a016ab0e5302a4ec22dadd14d453ab28b9e65f                                                                         0.0s
 => => naming to docker.io/library/docker-taskmanager:latest                                                                                                                   0.0s
 => => unpacking to docker.io/library/docker-taskmanager:latest                                                                                                                0.0s
 => [jobmanager] exporting to image                                                                                                                                            0.1s
 => => exporting layers                                                                                                                                                        0.0s
 => => exporting manifest sha256:a907c780d76d21d74fb34128850284cb3b7c95fbdc4cfd97aa6929f6c87bfce9                                                                              0.0s
 => => exporting config sha256:e6c82652b45617a085003dee1de0d6dd0f79a6e158958c111f8c7f3d8702df44                                                                                0.0s
 => => exporting attestation manifest sha256:ff7930ba2b290ff298216fa776815dc04bf43904d420a83bff7e4894381e62ce                                                                  0.0s
 => => exporting manifest list sha256:cc5d44dc6cbb4be37c68f591eee204353a355cadc3c5aa6e68071905e22c955e                                                                         0.0s
 => => naming to docker.io/library/docker-jobmanager:latest                                                                                                                    0.0s
 => => unpacking to docker.io/library/docker-jobmanager:latest                                                                                                                 0.0s
 => [taskmanager] resolving provenance for metadata file                                                                                                                       0.0s
 => [jobmanager] resolving provenance for metadata file                                                                                                                        0.0s
[+] Building 2/2
 ✔ jobmanager   Built                                                                                                                                                          0.0s
 ✔ taskmanager  Built
```

```bash
docker compose up -d

# Output
docker compose build
[+] Building 1.8s (14/14) FINISHED
 => [internal] load local bake definitions                                                                                                                                     0.0s
 => => reading from stdin 856B                                                                                                                                                 0.0s
 => [taskmanager internal] load build definition from Dockerfile                                                                                                               0.0s
 => => transferring dockerfile: 1.49kB                                                                                                                                         0.0s
 => [taskmanager internal] load metadata for docker.io/library/flink:1.19.0-scala_2.12                                                                                         0.9s
 => [taskmanager internal] load .dockerignore                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                0.0s
 => [taskmanager 1/6] FROM docker.io/library/flink:1.19.0-scala_2.12@sha256:61355051b493c0b2784ae5755608798e7c54d9db0f8467e9e3f183e3a48e617a                                   0.0s
 => => resolve docker.io/library/flink:1.19.0-scala_2.12@sha256:61355051b493c0b2784ae5755608798e7c54d9db0f8467e9e3f183e3a48e617a                                               0.0s
 => CACHED [taskmanager 2/6] RUN apt-get update -y &&     apt-get install -y python3 python3-pip python3-dev openjdk-11-jdk-headless &&     rm -rf /var/lib/apt/lists/*        0.0s
 => CACHED [taskmanager 3/6] RUN ln -s /usr/bin/python3 /usr/bin/python                                                                                                        0.0s
 => CACHED [taskmanager 4/6] RUN mkdir -p /opt/java &&     ln -s /usr/lib/jvm/java-11-openjdk-arm64 /opt/java/openjdk                                                          0.0s
 => CACHED [taskmanager 5/6] RUN pip3 install --no-cache-dir     apache-flink==1.19.0     psycopg2-binary                                                                      0.0s
 => CACHED [taskmanager 6/6] RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.19/flink-sql-connector-kafka  0.0s
 => [taskmanager] exporting to image                                                                                                                                           0.1s
 => => exporting layers                                                                                                                                                        0.0s
 => => exporting manifest sha256:a907c780d76d21d74fb34128850284cb3b7c95fbdc4cfd97aa6929f6c87bfce9                                                                              0.0s
 => => exporting config sha256:e6c82652b45617a085003dee1de0d6dd0f79a6e158958c111f8c7f3d8702df44                                                                                0.0s
 => => exporting attestation manifest sha256:2b10d3b8e076d577f4fee9ef58db141104acad06cecf0491f1adfbde29e70371                                                                  0.0s
 => => exporting manifest list sha256:c94948813cfdb9f708dc1c7317a016ab0e5302a4ec22dadd14d453ab28b9e65f                                                                         0.0s
 => => naming to docker.io/library/docker-taskmanager:latest                                                                                                                   0.0s
 => => unpacking to docker.io/library/docker-taskmanager:latest                                                                                                                0.0s
 => [jobmanager] exporting to image                                                                                                                                            0.1s
 => => exporting layers                                                                                                                                                        0.0s
 => => exporting manifest sha256:a907c780d76d21d74fb34128850284cb3b7c95fbdc4cfd97aa6929f6c87bfce9                                                                              0.0s
 => => exporting config sha256:e6c82652b45617a085003dee1de0d6dd0f79a6e158958c111f8c7f3d8702df44                                                                                0.0s
 => => exporting attestation manifest sha256:ff7930ba2b290ff298216fa776815dc04bf43904d420a83bff7e4894381e62ce                                                                  0.0s
 => => exporting manifest list sha256:cc5d44dc6cbb4be37c68f591eee204353a355cadc3c5aa6e68071905e22c955e                                                                         0.0s
 => => naming to docker.io/library/docker-jobmanager:latest                                                                                                                    0.0s
 => => unpacking to docker.io/library/docker-jobmanager:latest                                                                                                                 0.0s
 => [taskmanager] resolving provenance for metadata file                                                                                                                       0.0s
 => [jobmanager] resolving provenance for metadata file                                                                                                                        0.0s
[+] Building 2/2
 ✔ jobmanager   Built                                                                                                                                                          0.0s
 ✔ taskmanager  Built                                                                                                                                                          0.0s
niteshmishra@Mac docker % clear
niteshmishra@Mac docker % docker compose up -d
[+] Running 28/28
 ✔ redpanda-console Pulled                                                                                                                                                    18.1s
   ✔ edb6bdbacee9 Pull complete                                                                                                                                                2.9s
   ✔ 14ee393e44da Pull complete                                                                                                                                                0.4s
   ✔ 3435b9b0f2e8 Pull complete                                                                                                                                               15.5s
   ✔ 4fa930a9b4e0 Pull complete                                                                                                                                                0.8s
   ✔ 5793ecade4d8 Pull complete                                                                                                                                                1.1s
   ✔ 4912f5d8102b Pull complete                                                                                                                                               15.4s
   ✔ 7f1fcdde94d6 Pull complete                                                                                                                                                0.7s
 ✔ airflow Pulled                                                                                                                                                             31.8s
   ✔ 4f4fb700ef54 Pull complete                                                                                                                                                0.0s
   ✔ e4452321e08c Pull complete                                                                                                                                                0.4s
   ✔ 3984aafc07fc Pull complete                                                                                                                                                0.5s
   ✔ c6b48fae6983 Pull complete                                                                                                                                               14.9s
   ✔ 089aae753786 Pull complete                                                                                                                                                0.6s
   ✔ 32233c93bb41 Pull complete                                                                                                                                               14.9s
   ✔ 2793ead36c2e Pull complete                                                                                                                                                0.4s
   ✔ 378653a954b6 Pull complete                                                                                                                                                0.8s
   ✔ 27f691a99b0c Pull complete                                                                                                                                                0.5s
   ✔ 7558339e0596 Pull complete                                                                                                                                               27.7s
   ✔ 91a731a69931 Pull complete                                                                                                                                                0.5s
   ✔ dc25fc5f1fb6 Pull complete                                                                                                                                                0.5s
   ✔ 67a6f5e321ce Pull complete                                                                                                                                               29.1s
   ✔ f82d1d774736 Pull complete                                                                                                                                                0.5s
   ✔ ea3c6ffe6386 Pull complete                                                                                                                                               21.5s
   ✔ e1c43daa730d Pull complete                                                                                                                                                0.4s
   ✔ c4eea9d2baea Pull complete                                                                                                                                               28.8s
   ✔ 928ad8cafc4b Pull complete                                                                                                                                                0.5s
   ✔ 854e1d8c4c9c Pull complete                                                                                                                                               21.0s
[+] Running 7/7
 ✔ Network docker_default            Created                                                                                                                                   0.3s
 ✔ Container redpanda                Started                                                                                                                                   1.8s
 ✔ Container postgres                Started                                                                                                                                   1.8s
 ✔ Container omnistream-jobmanager   Started                                                                                                                                   1.8s
 ✔ Container omnistream-taskmanager  Started                                                                                                                                   1.4s
 ✔ Container redpanda-console        Started                                                                                                                                   1.5s
 ✔ Container omnistream-airflow      Started                                                                                                                                   1.3s

```

![Docker app container ss](../08-capstone/images/docker_app_container_ss.png)

### The Health Check
Wait about 20 seconds for Airflow and Flink to initialize their internal databases, then open your browser to these three tabs:

Redpanda Console: http://localhost:8082

Check: On overview page- it should show Brokers online 1 of 1

![ss](../08-capstone/images/Redpanda_console_showing_broker_running.png)


Flink Dashboard: http://localhost:8081

Check: Look for Task Managers. It should show 1 manager with 2 slots available.

![ss](../08-capstone/images/Flink_dashboard.png)

Airflow UI: http://localhost:8080

Check: Log in with admin / admin. It might take a moment to load the first time as it sets up its metadata in the Postgres container

![ss](../08-capstone/images/Airflow_UI.png)

### Test the Pipeline (The "Smoke Test")
Since your producers folder is ready, let's see if your Mac can talk to the Docker cluster. Open a new terminal tab, go to your root 08-capstone folder, and try to run one of your producers:

```Bash
# 1. Install local dependencies (if not already done)
pip install -r producers/requirements.txt


# 2. Run the aviation producer
python producers/aviation_producer.py
```
Once you run that, flip back to the Redpanda Console (8082). Do you see a new topic named aviation_events (or similar) appearing with live data?

