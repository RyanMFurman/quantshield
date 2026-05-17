# QuantShield

![Status](https://img.shields.io/badge/status-active_development-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![AWS](https://img.shields.io/badge/cloud-AWS-orange)
![Python](https://img.shields.io/badge/backend-Python-yellow)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Cloud-Native Financial Security Operations Platform built with AWS, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

## What This Project Does

QuantShield simulates a cloud SOC for a boutique quantitative trading firm. The platform combines real infrastructure, telemetry, detection logic, and operational APIs into a production-style portfolio system.

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

Expected output fields include:

- `events_evaluated`
- `alerts_generated`
- `alerts_inserted`
- `response_actions_triggered`

## Tests

```bash
python3 -m pytest -q tests/test_detection_engine.py tests/test_api.py
```

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
