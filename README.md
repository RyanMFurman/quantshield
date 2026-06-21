# QuantShield

![Status](https://img.shields.io/badge/status-active_development-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![AWS](https://img.shields.io/badge/cloud-AWS-orange)
![Python](https://img.shields.io/badge/backend-Python-yellow)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![License](https://img.shields.io/badge/license-MIT-green)

IAM Threat Detection Lab for a simulated quant trading firm, built with AWS-oriented architecture, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

## Live Demo

Public demo URLs:

- Dashboard: `https://demo.example.com`
- API health: `https://api.example.com/health`
- Insider risk API: `https://api.example.com/api/v1/insider-risk`

Replace the example domains after the AWS host, DNS, and HTTPS setup are complete.

## What This Project Does

QuantShield simulates the identity-security monitoring environment of a boutique quantitative trading firm. It is a Dockerized IAM threat detection lab with CloudTrail-style telemetry, identity-risk alerts, insider-risk correlation, and analyst triage workflows.

The lab focuses on high-value identity and data-access risks that matter in financial research environments:

- IAM privilege escalation
- access key creation
- root account activity
- MFA disablement
- privileged role assumption
- S3 research-data access
- abnormal market-data context around sensitive activity

The main demo story:

> A simulated quant analyst account creates an access key, assumes a privileged trading role, attaches administrative access, touches NVDA research data in S3, and disables MFA. QuantShield correlates the IAM telemetry with abnormal NVDA market movement and raises identity-risk and insider-risk alerts for analyst triage.

## Live Demo Architecture

```text
Internet
  |
  v
EC2 app host
  |-- Nginx + HTTPS
  |-- Docker Compose
  |-- FastAPI API
  |-- Streamlit SOC dashboard
  |
  v
RDS PostgreSQL
  |-- market_prices
  |-- security_events
  |-- alerts
  |-- insider_risk_findings
```

The v1 live demo intentionally avoids NAT Gateway, ALB, autoscaling, and Kubernetes
so the project can stay comfortable under a small monthly AWS budget.

## Noah SOC Scope

Implemented detection-and-response core focused on cloud SOC workflows:

- Detection engine with DB cycle support: read events, evaluate rules, deduplicate OPEN alerts, write alerts
- MITRE-mapped rules:
  - Brute force (`T1110`)
  - IAM identity risk (`T1098`)
  - Privilege escalation (`T1078.004`)
  - Lateral movement (`T1021`)
  - Data exfiltration (`T1567`)
- CloudTrail-style IAM simulator for local identity attack scenarios
- Minimal incident response hook for P1 alerts (structured response actions for triage)
- API visibility for SOC operations:
  - Active alerts
  - Recent security events
  - Detection summary by rule and severity
- Unit tests for rule behavior, dedup logic, responder behavior, and DB-cycle smoke path

## API Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

Available routes:

- `GET /health`
- `GET /market/latest`
- `GET /alerts/active`
- `GET /api/v1/alerts/active`
- `GET /api/v1/events/recent`
- `GET /api/v1/detections/summary`
- `GET /api/v1/insider-risk`

Set `DATABASE_URL` for DB-backed routes.

## Full Local Demo

Run the complete local stack with PostgreSQL, seeded market/security data,
CloudTrail-style IAM telemetry, FastAPI, Streamlit, identity-risk alerts, and
insider-risk findings:

```bash
docker compose up --build
```

Start Docker Desktop first. If Docker is not running, Windows may report that
`dockerDesktopLinuxEngine` cannot be found.

Open:

- Dashboard: `http://localhost:8501`
- API index: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Insider risk API: `http://localhost:8000/api/v1/insider-risk`

Refresh demo data manually:

```bash
docker compose run --rm demo-seed
```

## Detection Engine Quickstart

Run local demo (no DB required):

```bash
python3 scripts/run_detection_demo.py
```

Run detection engine DB cycle (requires `DATABASE_URL`):

```bash
python3 scripts/run_detection_db_cycle.py
```

Run insider-risk analysis DB cycle (requires `DATABASE_URL`):

```bash
python3 scripts/run_insider_risk_analysis.py
```

Seed the live demo scenario and run both detection cycles (requires `DATABASE_URL`):

```bash
python3 scripts/seed_live_demo_data.py
```

Expected output fields include:

- `events_evaluated`
- `alerts_generated`
- `alerts_inserted`
- `response_actions_triggered`
- `findings_generated`
- `findings_inserted`
- `market_rows_inserted`
- `security_events_upserted`

## Tests

```bash
python3 -m pytest -q tests/test_detection_engine.py tests/test_api.py
```

## Live Demo Deployment

See `docs/live-demo-aws.md` for the EC2, Docker Compose, Nginx, and RDS-backed
demo runbook. See `docs/live-rds-app-config.md` for live database and app
environment configuration.

## Resume Summary

Built a Dockerized IAM threat detection lab for a simulated quant trading firm
using AWS-oriented architecture, Terraform, Python, PostgreSQL, FastAPI, Docker,
and Streamlit to simulate CloudTrail-style telemetry, identity-risk alerts,
insider-risk correlation, and analyst triage workflows.

## Current Progress

### Completed

- Terraform networking foundation
- PostgreSQL schema + seed data
- FastAPI backend skeleton routes
- Detection engine phase 2 (4 rules + dedup + DB cycle + response hook)
- Detection and API tests

### In Progress

- IAM module
- Cloud security integrations (GuardDuty / CloudTrail)
- Dashboard enhancements

## Disclaimer

QuantShield is a simulated educational and portfolio environment designed to demonstrate engineering capability. It is not connected to live financial systems.
