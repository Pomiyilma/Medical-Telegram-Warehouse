# Enterprise Medical Commerce ELT & Vision Platform

A production-grade data engineering pipeline built to scrape distributed public Ethiopian pharmaceutical, cosmetic, and medical supply channel feeds, centralize raw objects into an immutable storage lake, and transform data assets into an analytics-ready Star Schema using PostgreSQL, dbt, and YOLOv8 computer vision classification engines.

## 🏗️ Technical Architecture Matrix

```text
[ Telegram Channels ] ──(Telethon Async API)──> [ Immutable Local Data Lake ]
                                                            │
                                                     (psycopg2 Bulk)
                                                            ▼
[ FastAPI App Tier ]                               [ PostgreSQL Database ]
   ├── /top-products                                  ├── raw.telegram_messages
   ├── /channels/activity                             └── raw.yolo_detections
   └── /reports/visual-content                              │
         ▲                                            (dbt Core Core)
         └───────(Analytical Mart SQL Views)───────────┴──> dev.fct_messages
                                                           dev.fct_image_detections

--> Core Technology Components

- Orchestration Layer: Managed via Dagster as Software-Defined Operations, enforcing strict execution dependencies and automated tracking.

- Computer Vision Enrichment: Integrated with a YOLOv8 nano framework to categorize incoming promotional and display imagery.

- Transformation Engineering: Built using dbt (data build tool) to decouple staging queries and materialize dimensional models (dim_channels, dim_dates, fct_messages, fct_image_detections).

- Data Product Delivery: Exposes sub-second analytical queries to client consumers through a high-performance FastAPI REST engine.


--> Production Execution Controls

1. Initialize Pipeline Infrastructure
Ensure your active virtual environment is loaded, then install dependencies and check data transformations connectivity:

Run dependencies build
pip install -r requirements.txt

Run dbt verification checks
cd medical_warehouse && dbt debug && dbt compile && cd ..

2. Launch the Orchestrated Ingestion DAG
Trigger the unified pipeline framework to execute the end-to-end scraper, loader, YOLO sweeps, and dbt models automatically under Dagster supervision:

dagster dev -f pipeline.py
Access the live graphical monitoring interface dashboard at http://localhost:3000.

3. Expose the Analytical Application Layer
Run the high-performance FastAPI backend server to serve analytical endpoints and interactive API documentation:

uvicorn api.main:app --reload
Access the auto-generated Swagger UI testing sandbox dashboard directly at http://127.0.0.1:8000/docs.

--> Data Quality Governance & Testing

Data protection and warehouse consistency are strictly maintained through automated dbt testing suites:

- Primary Constraints: unique and not_null assertions applied across key attributes.
- Relational Integrity: Hard relationships validation linking facts directly back to core lookups.
- Custom Business Rules: Custom test scripts (assert_no_future_messages.sql) intercept and block anomalous record dates before data enters production.