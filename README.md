# QuantShield

![Status](https://img.shields.io/badge/status-active_development-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![AWS](https://img.shields.io/badge/cloud-AWS-orange)
![Python](https://img.shields.io/badge/backend-Python-yellow)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Cloud-Native Financial Security Operations Platform built with AWS, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

## Live Demo

Public demo URLs:

- Dashboard: `https://demo.example.com`
- API health: `https://api.example.com/health`
- Insider risk API: `https://api.example.com/api/v1/insider-risk`

Replace the example domains after the AWS host, DNS, and HTTPS setup are complete.

## What This Project Does

QuantShield simulates a cloud SOC for a boutique quantitative trading firm. The platform combines real infrastructure, telemetry, detection logic, and operational APIs into a production-style portfolio system.

The main demo story:

> QuantShield detects unusual activity around NVDA: abnormal trading volume, failed login attempts from a trading-service account, and S3 data access from the same time window. The Market Insider Risk Analyzer correlates the activity and raises an insider-risk finding.

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
  - Privilege escalation (`T1078.004`)
  - Lateral movement (`T1021`)
  - Data exfiltration (`T1567`)
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

Built a cloud-native financial security operations platform using AWS, Terraform,
Python, PostgreSQL, FastAPI, Docker, and Streamlit to simulate market telemetry
ingestion, threat detection engineering, insider-risk analysis, and SOC-style
incident workflows.

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
