# Shell Retail Intelligence

Databricks App bundle for a Shell retail performance, pricing, promotion, customer, and data-quality dashboard. The UI is built with Dash and Plotly and can run locally with deterministic mock data or connect to Databricks SQL and AI/BI Genie.

## Features

- Network and regional performance KPIs
- Station portfolio and campaign analysis
- Customer loyalty and pricing insights
- What-if campaign scenario planning
- Databricks AI/BI Genie questions
- Data catalog and freshness views
- SCD2 and data-quality monitoring

## Project Structure

```text
.
├── databricks.yml                         # Databricks bundle definition
├── resources/
│   └── shell_retail_analytics.app.yml     # Databricks App resource
└── src/app/
    ├── app.py                             # Dash application entry point
    ├── app.yaml                           # App command and environment
    ├── backend.py                         # Databricks SQL data access
    ├── backend_mock.py                    # Local deterministic mock data
    ├── genie_helper.py                    # AI/BI Genie integration
    └── requirements.txt                   # App dependencies
```

## Prerequisites

- Python 3.10 or later
- Databricks CLI installed and authenticated for deployment
- Access to the configured Databricks workspace and SQL warehouse for live data

## Run Locally

Create and activate a virtual environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\app\requirements.txt dash plotly pandas numpy
```

Start the dashboard with mock data:

```powershell
cd src\app
$env:USE_MOCK_BACKEND = "true"
python app.py
```

Open [http://localhost:8050](http://localhost:8050). The default port is `8050`; set `PORT` to use another port. Set `DEBUG=true` to enable Dash debug mode.

## Live Databricks Data

To use the SQL backend locally, authenticate the Databricks SDK using your normal local profile or environment-based authentication, then run:

```powershell
$env:USE_MOCK_BACKEND = "false"
$env:DATABRICKS_HOST = "https://dbc-b7c54f7a-7524.cloud.databricks.com"
$env:DATABRICKS_SQL_WAREHOUSE_ID = "e2f2719979a11f9d"
python app.py
```

The live backend reads from the `workspace.retail_store` catalog and schema. When a query fails or a required table is unavailable, supported views fall back to mock data.

For Genie support, configure a Databricks token through the authentication mechanism used by your environment. Do not commit tokens or other secrets to this repository.

## Deploy as a Databricks App

Validate and deploy the bundle to the configured `free` target:

```powershell
databricks bundle validate -t free
databricks bundle deploy -t free
```

The bundle provisions or updates the `shell-retail-analytics` app using `src/app` as its source path. The app command and default environment variables are defined in [src/app/app.yaml](src/app/app.yaml).

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `USE_MOCK_BACKEND` | `true` | Select mock data when true; use Databricks SQL when false |
| `DATABRICKS_HOST` | Configured workspace URL | Databricks workspace host |
| `DATABRICKS_SQL_WAREHOUSE_ID` | `e2f2719979a11f9d` | SQL warehouse used by the live backend |
| `PORT` | `8050` | Local or app HTTP port |
| `DEBUG` | `false` | Enable Dash debug mode |

## Notes

- Mock data is seeded for repeatable local development.
- The application binds to `0.0.0.0` so it can run inside a Databricks App.
- Keep credentials outside source control and use Databricks-native authentication in deployed environments.