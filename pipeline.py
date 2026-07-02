import subprocess
import os
from dagster import op, job, schedule, ScheduleDefinition, Definitions

# Helper function to safely execute shell terminal commands from the project root
def execute_shell_command(command: str, working_dir: str = "."):
    print(f"🚀 Running Orchestration Step: {command}")
    result = subprocess.run(command, shell=True, cwd=working_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"❌ Execution Failure in Command: {command}\nError Output: {result.stderr}")
    print(result.stdout)
    return True

# --- Op 1: Scrape Telegram Data Feed ---
@op(description="Trigger Telethon script to pull recent medical messages and media objects from public channels.")
def scrape_telegram_data():
    execute_shell_command("python -m src.scraper")

# --- Op 2: Ingest Raw Data into Postgres ---
@op(description="Bulk load structural data lake JSON documents into PostgreSQL landing schema.")
def load_raw_to_postgres(upstream_done):
    execute_shell_command("python scripts/load_to_postgres.py")

# --- Op 3: Execute dbt Core Core Transformations ---
@op(description="Compile and run dbt model definitions to create staging views and star schema marts.")
def run_dbt_transformations(upstream_done):
    # This must explicitly run inside your dbt project folder where dbt_project.yml lives
    execute_shell_command("dbt run", working_dir="medical_warehouse")

# --- Op 4: Run YOLO Computer Vision Sweeps ---
@op(description="Execute YOLOv8 nano object detection on newly arrived data lake images and load to DB.")
def run_yolo_enrichment(upstream_done):
    execute_shell_command("python -m src.yolo_detect")
    execute_shell_command("python scripts/load_yolo_to_postgres.py")

# --- Op 5: Refresh dbt Analytical View Joins ---
@op(description="Re-run dbt models to materialize final fct_image_detections data products.")
def refresh_dbt_marts(upstream_done):
    execute_shell_command("dbt run", working_dir="medical_warehouse")

# --- Build the Orchestrated Graph Pipeline ---
@job(name="medical_data_platform_pipeline", description="End-to-end data platform engine for Kara Solutions.")
def medical_data_pipeline():
    # Enforce precise sequential tracking dependencies
    scraped = scrape_telegram_data()
    loaded = load_raw_to_postgres(scraped)
    dbt_base = run_dbt_transformations(loaded)
    yolo_done = run_yolo_enrichment(dbt_base)
    refresh_dbt_marts(yolo_done)

# --- Add Production Automated Daily Scheduling ---
daily_pipeline_schedule = ScheduleDefinition(
    job=medical_data_pipeline,
    cron_schedule="0 0 * * *", # Runs automatically every night at midnight
    execution_timezone="Africa/Addis_Ababa"
)

# --- THE FIX: Define the explicit Dagster code repository exposure ---
defs = Definitions(
    jobs=[medical_data_pipeline],
    schedules=[daily_pipeline_schedule]
)
