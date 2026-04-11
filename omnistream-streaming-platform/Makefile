SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# -------------------------------
# Paths
# -------------------------------
PROJECT_ROOT := $(CURDIR)
DOCKER_DIR := $(PROJECT_ROOT)/docker
FLINK_DIR := $(PROJECT_ROOT)/flink-processor
VENV_DIR := $(PROJECT_ROOT)/.venv
TERRAFORM_DIR := $(PROJECT_ROOT)/terraform

PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

JAR_NAME := flink-processor-1.0-SNAPSHOT.jar
JAR_PATH_IN_CONTAINER := /opt/flink/project/target/$(JAR_NAME)

# -------------------------------
# Producers
# -------------------------------
AVIATION_DIR := $(PROJECT_ROOT)/producers/aviation
FINANCE_DIR := $(PROJECT_ROOT)/producers/finance
GEO_DIR := $(PROJECT_ROOT)/producers/geo

AVIATION_PRODUCER := $(AVIATION_DIR)/producer.py
FINANCE_PRODUCER := $(FINANCE_DIR)/producer.py
GEO_PRODUCER := $(GEO_DIR)/producer.py

AVIATION_REQUIREMENTS := $(AVIATION_DIR)/requirements.txt
FINANCE_REQUIREMENTS := $(FINANCE_DIR)/requirements.txt
GEO_REQUIREMENTS := $(GEO_DIR)/requirements.txt

# -------------------------------
# Demo settings
# -------------------------------
AVIATION_MAX_RECORDS ?= 40

FINANCE_SYMBOLS ?= IBM
FINANCE_MAX_RECORDS ?= 3
FINANCE_MAX_EMPTY_POLLS ?= 2
FINANCE_SYMBOL_DELAY_SECONDS ?= 12

GEO_MAX_RECORDS ?= 10
GEO_MAX_EMPTY_POLLS ?= 3

# -------------------------------
# Phony targets
# -------------------------------
.PHONY: help venv install-producers docker-up docker-down \
        flink-build flink-wait flink-cancel flink-submit flink-logs \
        reset-topics reset-demo producers-demo demo destroy kill-producers \
        terraform-destroy terraform-apply \
        dbt-debug dbt-run dbt-test dbt-build \
        wait-redpanda wait-bq \
        check-gcp-auth check-gcp-project

# -------------------------------
# Help
# -------------------------------
help:
	@echo ""
	@echo "Available commands:"
	@echo "  make demo             - Full pipeline demo"
	@echo "  make producers-demo   - Run producers only"
	@echo "  make reset-demo       - Cancel Flink jobs + delete topics"
	@echo "  make kill-producers   - Kill local producer processes"
	@echo "  make destroy          - Tear down everything"
	@echo "  make dbt-debug        - Check dbt connection/profile"
	@echo "  make dbt-run          - Run dbt models"
	@echo "  make dbt-test         - Run dbt tests"
	@echo "  make dbt-build        - Run dbt build"
	@echo ""

# -------------------------------
# Python Virtual Environment
# -------------------------------
venv:
	@test -d "$(VENV_DIR)" || python3 -m venv "$(VENV_DIR)"
	@echo "Virtual environment ready."

install-producers: venv
	@echo "Installing producer dependencies..."
	@"$(PIP)" install --upgrade pip
	@if [ -f "$(AVIATION_REQUIREMENTS)" ]; then "$(PIP)" install -r "$(AVIATION_REQUIREMENTS)"; fi
	@if [ -f "$(FINANCE_REQUIREMENTS)" ]; then "$(PIP)" install -r "$(FINANCE_REQUIREMENTS)"; fi
	@if [ -f "$(GEO_REQUIREMENTS)" ]; then "$(PIP)" install -r "$(GEO_REQUIREMENTS)"; fi
	@echo "Producer dependencies installed."

# -------------------------------
# Docker
# -------------------------------
docker-up:
	@cd "$(DOCKER_DIR)" && docker compose up -d

docker-down:
	@cd "$(DOCKER_DIR)" && docker compose down

# -------------------------------
# Flink Build
# -------------------------------
flink-build:
	@cd "$(FLINK_DIR)" && mvn clean package -DskipTests

# -------------------------------
# Flink Wait
# -------------------------------
flink-wait:
	@echo "Waiting for Flink REST API..."
	@until curl -sf http://localhost:8081/overview > /dev/null; do \
		echo "Flink REST not ready yet..."; \
		sleep 5; \
	done
	@echo "Flink REST is up."

	@echo "Waiting for TaskManager registration..."
	@until python3 -c 'import json,sys; data=json.load(sys.stdin); sys.exit(0 if data.get("taskmanagers") else 1)' < <(curl -sf http://localhost:8081/taskmanagers); do \
		echo "No TaskManager registered yet..."; \
		sleep 5; \
	done
	@echo "TaskManager is registered."

# -------------------------------
# Cancel Flink Jobs
# -------------------------------
flink-cancel:
	@echo "Canceling any running Flink jobs..."
	@resp=$$(curl -sf http://localhost:8081/jobs/overview 2>/dev/null || true); \
	jobs=$$(printf '%s' "$$resp" | python3 -c 'import sys, json; s=sys.stdin.read().strip(); \
print("\n".join(j["jid"] for j in json.loads(s).get("jobs", [])) if s.startswith("{") else "")' 2>/dev/null || true); \
	if [ -n "$$jobs" ]; then \
		for j in $$jobs; do \
			echo "Canceling job $$j"; \
			curl -sf -X PATCH http://localhost:8081/jobs/$$j > /dev/null || true; \
		done; \
	else \
		echo "No running jobs found."; \
	fi
	@sleep 3

# -------------------------------
# Submit Flink Job
# -------------------------------
flink-submit: flink-wait
	@echo "Submitting Flink job..."
	@docker exec omnistream-jobmanager /opt/flink/bin/flink run -d "$(JAR_PATH_IN_CONTAINER)"

# -------------------------------
# Logs
# -------------------------------
flink-logs:
	@docker logs omnistream-jobmanager --tail 100
	@docker logs omnistream-taskmanager --tail 100

# -------------------------------
# Reset Redpanda Topics
# -------------------------------
reset-topics:
	@echo "Deleting all Redpanda topics..."
	@topics=$$(docker exec redpanda rpk topic list 2>/dev/null | tail -n +2 | awk '{print $$1}' || true); \
	if [ -n "$$topics" ]; then \
		for t in $$topics; do \
			echo "Deleting topic $$t"; \
			docker exec redpanda rpk topic delete "$$t" || true; \
		done; \
	else \
		echo "No topics found."; \
	fi

reset-demo: flink-cancel reset-topics
	@echo "Demo environment reset complete."

# -------------------------------
# Wait Redpanda to be ready
# -------------------------------
wait-redpanda:
	@until python3 -c 'import socket; s=socket.socket(); s.settimeout(1); s.connect(("127.0.0.1",19092)); s.close()' 2>/dev/null; do \
		echo "Waiting for Redpanda on localhost:19092..."; \
		sleep 3; \
	done
	@echo "Redpanda is ready."

# -------------------------------
# Kill local producer processes
# -------------------------------
kill-producers:
	@echo "Killing local producer processes if running..."
	@pkill -f "$(AVIATION_PRODUCER)" || true
	@pkill -f "$(FINANCE_PRODUCER)" || true
	@pkill -f "$(GEO_PRODUCER)" || true
	@echo "Producer cleanup done."

# -------------------------------
# Terraform Destroy
# -------------------------------
terraform-destroy:
	@echo "Destroying Terraform-managed infrastructure..."
	@if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd "$(TERRAFORM_DIR)" && terraform destroy -auto-approve; \
	else \
		echo "Terraform directory not found. Skipping."; \
	fi

# -------------------------------
# Terraform Apply
# -------------------------------
terraform-apply:
	@echo "Applying Terraform-managed infrastructure..."
	@cd "$(TERRAFORM_DIR)" && terraform apply -auto-approve

# -------------------------------
# Producers Demo
# -------------------------------
producers-demo: wait-redpanda install-producers
	@echo "Running aviation producer..."
	@MAX_RECORDS="$(AVIATION_MAX_RECORDS)" "$(PYTHON)" "$(AVIATION_PRODUCER)"

	@echo "Running finance producer..."
	@DEMO_MODE=true \
	FINANCE_SYMBOLS="$(FINANCE_SYMBOLS)" \
	MAX_RECORDS="$(FINANCE_MAX_RECORDS)" \
	MAX_EMPTY_POLLS="$(FINANCE_MAX_EMPTY_POLLS)" \
	FINANCE_SYMBOL_DELAY_SECONDS="$(FINANCE_SYMBOL_DELAY_SECONDS)" \
	"$(PYTHON)" "$(FINANCE_PRODUCER)"

	@echo "Running geo producer..."
	@MAX_RECORDS="$(GEO_MAX_RECORDS)" \
	MAX_EMPTY_POLLS="$(GEO_MAX_EMPTY_POLLS)" \
	"$(PYTHON)" "$(GEO_PRODUCER)"

	@echo "All demo producers completed."

# -------------------------------
# dbt
# -------------------------------
dbt-debug:
	@echo "Running dbt debug..."
	@docker exec omnistream-airflow bash -c "cd /opt/airflow/dbt && dbt debug --profiles-dir ."

dbt-run:
	@echo "Running dbt run..."
	@docker exec omnistream-airflow bash -c "cd /opt/airflow/dbt && dbt run --profiles-dir ."

dbt-test:
	@echo "Running dbt test..."
	@docker exec omnistream-airflow bash -c "cd /opt/airflow/dbt && dbt test --profiles-dir ."

dbt-build:
	@echo "Running dbt build..."
	@docker exec omnistream-airflow bash -c "cd /opt/airflow/dbt && dbt build --profiles-dir ."

# -------------------------------
# Wait for BigQuery data
# -------------------------------
wait-bq:
	@echo "Waiting for data to land in BigQuery staging..."
	@for i in $$(seq 1 24); do \
		AVIATION_COUNT=$$(bq query --quiet --nouse_legacy_sql --format=csv \
			"SELECT COUNT(*) FROM \`de-zoomcamp-2026-486900.omnistream_staging.raw_aviation_data\`" | tail -n 1); \
		FINANCE_COUNT=$$(bq query --quiet --nouse_legacy_sql --format=csv \
			"SELECT COUNT(*) FROM \`de-zoomcamp-2026-486900.omnistream_staging.raw_finance_data\`" | tail -n 1); \
		GEO_COUNT=$$(bq query --quiet --nouse_legacy_sql --format=csv \
			"SELECT COUNT(*) FROM \`de-zoomcamp-2026-486900.omnistream_staging.raw_geo_data\`" | tail -n 1); \
		echo "BQ counts -> aviation=$$AVIATION_COUNT finance=$$FINANCE_COUNT geo=$$GEO_COUNT"; \
		if [ "$$AVIATION_COUNT" -gt 0 ] && [ "$$FINANCE_COUNT" -gt 0 ] && [ "$$GEO_COUNT" -gt 0 ]; then \
			echo "✅ BigQuery staging has data."; \
			exit 0; \
		fi; \
		sleep 10; \
	done; \
	echo "❌ Timed out waiting for BigQuery staging data."; \
	exit 1

# -------------------------------
# Validate GCP Auth
# -------------------------------
check-gcp-auth:
	@echo "Checking GCP authentication..."
	@if ! bq ls >/dev/null 2>&1; then \
		echo "❌ GCP authentication not found."; \
		echo "👉 Run: gcloud auth application-default login"; \
		exit 1; \
	else \
		echo "✅ GCP authentication OK"; \
	fi

# -------------------------------
# Check GCP Project
# -------------------------------
check-gcp-project:
	@echo "Checking GCP project..."
	@PROJECT=$$(gcloud config get-value project 2>/dev/null); \
	if [ "$$PROJECT" != "de-zoomcamp-2026-486900" ]; then \
		echo "⚠️ Current project: $$PROJECT"; \
		echo "👉 Run: gcloud config set project de-zoomcamp-2026-486900"; \
		exit 1; \
	else \
		echo "✅ GCP project set correctly"; \
	fi

# -------------------------------
# Full Demo
# -------------------------------
demo: check-gcp-auth check-gcp-project flink-build terraform-apply docker-up flink-cancel flink-submit producers-demo wait-bq dbt-build
	@echo ""
	@echo "🎉 OmniStream Full Demo Completed!"
	@echo "Airflow UI: http://localhost:8080"
	@echo "Flink UI:   http://localhost:8081"
	@echo "Redpanda:   http://localhost:8082"
	@echo ""

# -------------------------------
# Destroy Everything
# -------------------------------
destroy:
	-@$(MAKE) flink-cancel
	-@$(MAKE) reset-topics
	-@$(MAKE) kill-producers
	-@cd "$(DOCKER_DIR)" && docker compose down -v
	-@$(MAKE) terraform-destroy
	@echo "Environment destroyed."