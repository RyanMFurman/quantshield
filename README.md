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

### Detection and Security (Current)

- Brute-force detection rule (MITRE T1110)
- Privilege escalation detection rule (MITRE T1078.004)
- Deduplication of OPEN alerts
- DB-backed detection cycle (read events -> evaluate rules -> insert alerts)
- Active alerts API endpoint

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

Set `DATABASE_URL` for API DB routes.

## Detection Engine Quickstart

Run local demo (no DB required):

```bash
python3 scripts/run_detection_demo.py
```

Run tests:

```bash
python3 -m pytest -q tests/test_detection_engine.py
```

## Current Progress

### Completed

- Terraform networking foundation
- PostgreSQL schema + seed data
- FastAPI backend skeleton routes
- Detection engine phase 1 (2 rules + dedup + DB cycle)
- Detection unit tests

### In Progress

- IAM module
- Cloud security integrations (GuardDuty / CloudTrail)
- Dashboard enhancements

## Disclaimer

QuantShield is a simulated educational and portfolio environment designed to demonstrate engineering capability. It is not connected to live financial systems.
