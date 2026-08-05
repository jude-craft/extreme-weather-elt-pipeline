# Extreme Weather ELT Pipeline

An automated Extract, Load, and Transform (ELT) data pipeline designed to fetch historical and daily weather data for Nairobi, Kenya. This project demonstrates modern data engineering practices by orchestrating a local-first containerized workflow that extracts data from a public API, loads it into a Google Cloud Storage (GCS) data lake, and appends it to a Google BigQuery data warehouse for analytical querying.

## Architecture & Tech Stack

* **Language:** Python 3.11
* **Infrastructure as Code (IaC):** Terraform
* **Containerization:** Docker & Docker Compose
* **Orchestration:** Kestra
* **Data Lake:** Google Cloud Storage (GCS)
* **Data Warehouse:** Google BigQuery
* **Data Source:** [Open-Meteo API](https://open-meteo.com/)

## Pipeline Workflow

1. **Extraction:** A Python script (`extract.py`) fetches daily weather metrics (minimum temperature, precipitation, wind speed, solar radiation, and evapotranspiration) from the Open-Meteo API.
2. **Data Lake Storage:** Kestra uploads the raw CSV output to a partitioned GCS bucket. The pipeline utilizes a Data Lake pattern, creating unique daily files (e.g., `nairobi_weather_2026-08-04_to_2026-08-04.csv`) rather than overwriting a single master file.
3. **Data Warehouse Loading:** Kestra triggers a BigQuery load job, appending the new daily records to the existing `raw_weather_data` table for persistent storage and downstream analytics.

## Project Structure

```text
EXTREME-WEATHER-ELT/
├── credentials/
│   └── gcp-service-account.json # Ignored via .gitignore for security
├── flows/
│   └── weather_elt_flow.yml     # Kestra orchestration declarative flow
├── terraform/
│   ├── main.tf                  # GCP Resource definitions
│   └── variable.tf              # Terraform variables
├── .env                         # Environment variables (Ignored in version control)
├── .env.example                 # Template for environment variables
├── .gitignore                   # Git tracking exclusions
├── docker-compose.yml           # Docker services configuration for Kestra
├── Dockerfile                   # Custom image configuration (if applicable)
├── extract.py                   # Python extraction logic
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies (e.g., requests)
```

## Prerequisites

To replicate or run this project locally, ensure you have the following installed:
* Git
* Docker and Docker Compose
* Terraform CLI
* Google Cloud SDK (`gcloud` CLI)
* A Google Cloud Platform (GCP) account with Billing Enabled.

## Setup and Configuration

### 1. Google Cloud Setup
1. Create a new GCP Project.
2. Create a Service Account with the following roles:
   * BigQuery Admin
   * Storage Admin
3. Generate a JSON key for the Service Account.
4. Save the downloaded JSON file into the `credentials/` directory as `gcp-service-account.json`.

### 2. Infrastructure Deployment (Terraform)
Navigate to the `terraform/` directory and deploy the required GCS bucket and BigQuery dataset.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```
*Note: Type `yes` when prompted by Terraform.*

### 3. Orchestration Setup (Kestra & Docker)
Ensure Docker is running on your machine. Start the Kestra server using Docker Compose.

```bash
docker compose up -d
```
Access the Kestra UI by navigating to `http://localhost:8080` in your web browser. 

### 4. Deploying the Flow
1. In the Kestra UI, navigate to the **Flows** tab.
2. Click **Create** and paste the contents of `flows/weather_elt_flow.yml`.
3. Save the flow. 
4. Ensure the variables in the Kestra flow (e.g., `gcp_project`, `gcs_bucket`) match the resources created by Terraform.

## Execution Options

The pipeline is designed to handle both historical backfilling and automated daily incremental loads.

* **Automated Daily Incremental Load:** The flow includes a Cron trigger (`0 1 * * *`). It will automatically run at 1:00 AM UTC every day. It dynamically calculates yesterday's date, extracts only that specific day's data, creates a new file in GCS, and appends the row to BigQuery.
* **Manual Backfill:** You can execute the flow manually from the Kestra UI. By passing specific `start_date` and `end_date` parameters (Format: YYYY-MM-DD), you can backfill historical data (e.g., 20 years of archive data) in a single run.

## Common Pitfalls & Troubleshooting

* **Terraform Bucket Destruction:** If you attempt to run `terraform destroy` to tear down the project, Terraform will fail if the GCS bucket contains CSV files. To resolve this, ensure `force_destroy = true` is set in your Terraform `google_storage_bucket` resource block, or manually empty the bucket via the GCP Console first.
* **Kestra Web UI Caching:** When triggering manual runs after previously running a backfill, the Kestra UI may pass empty strings instead of `null` values to the date parameters. The flow uses the Pebble ternary operator `? :` instead of the null-coalescing operator `??` to safely fall back to the dynamic daily date calculation.
* **Docker Out Of Memory (OOM) Errors:** If deploying Kestra on a machine or VM with limited RAM (e.g., 1GB), the Java Virtual Machine may crash. Ensure you configure memory limits (e.g., `JAVA_OPTS: "-Xms256m -Xmx512m"`) in the `docker-compose.yml` or allocate sufficient Swap space on your operating system.

## Future Enhancements
* Implement a robust dbt (data build tool) layer in BigQuery to transform the raw weather data into analytical star-schema models.
* Integrate data quality testing (e.g., Great Expectations) within the Kestra flow prior to BigQuery insertion.