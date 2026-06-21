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

## Contributor Scope

### Ryan AWS / IAM / Platform Scope

Built the AWS-oriented platform foundation that makes QuantShield credible as an
IAM/cloud security engineering project:

- Terraform-based AWS architecture plan for VPC, security groups, IAM, EC2 app
  host, RDS PostgreSQL, and deployment roles
- Docker Compose lab that runs FastAPI, Streamlit, PostgreSQL, schema setup, and
  deterministic demo seeding with no AWS spend required
- Live-demo runbooks for EC2, RDS, Nginx, HTTPS, environment configuration, and
  scheduled refresh
- FastAPI service layer for health, market data, alert, event, detection summary,
  and insider-risk APIs
- GitHub Actions CI for Python tests and smoke checks
- Clear local-to-AWS mapping from simulated CloudTrail telemetry to real AWS
  CloudTrail, EventBridge, S3, RDS, and IAM operations

### Noah SOC / Detection Engineering Scope

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

## AWS and IAM Skills Demonstrated

QuantShield is designed to show practical cloud security skills without requiring
reviewers to pay for AWS resources:

- IAM threat modeling for root use, MFA disablement, access keys, policy changes,
  role assumption, and suspicious S3 data access
- CloudTrail-style event modeling with realistic AWS event names and identity
  context
- PostgreSQL-backed alert and finding persistence
- API-first security telemetry access through FastAPI
- Analyst workflow design through Streamlit SOC views
- Dockerized local deployment and AWS-ready deployment documentation
- Infrastructure story covering EC2, RDS, security groups, IAM roles, Nginx,
  HTTPS, and scheduled demo refresh

## Realistic Security Framing

QuantShield does not claim to prove illegal insider trading. In a real financial
environment, a security tool would raise potential identity, data-access, and
MNPI exposure risk for human review. The project intentionally frames the
highest-risk scenario as insider-risk correlation:

- unusual market movement around a watched symbol
- access to symbol-specific research data
- suspicious identity activity in the same time window
- analyst triage of the combined signal

That framing is accurate, defensible, and stronger for IAM/security interviews
than claiming the app can determine legal intent.

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

## Portfolio Summary

Built a Dockerized IAM threat detection lab for a simulated quant trading firm
using AWS-oriented architecture, Terraform, Python, PostgreSQL, FastAPI, Docker,
and Streamlit to simulate CloudTrail-style telemetry, identity-risk alerts,
insider-risk correlation, and analyst triage workflows.

## Completed Capabilities

- Local Docker SOC lab with PostgreSQL, FastAPI, Streamlit, schema setup, and
  repeatable demo data
- CloudTrail-style IAM telemetry simulator
- IAM detections for root login, MFA disablement, access key creation,
  administrator policy attachment, and privileged role assumption
- Detection engine with alert deduplication and DB-cycle execution
- Insider-risk correlation that requires symbol-specific security context
- SOC dashboard with overview, IAM risk, insider risk, alerts, market, events,
  and system views
- AWS live-demo runbooks for EC2, RDS, Nginx, HTTPS, and scheduled refresh
- Python test coverage for API routes, detection rules, alert behavior, and
  insider-risk analysis

## Interview One-Liner

QuantShield is an IAM threat detection lab for a simulated quant trading firm:
it turns CloudTrail-style identity events and market/research-data context into
SOC alerts, insider-risk findings, and analyst triage workflows.

## Disclaimer

QuantShield is a simulated educational and portfolio environment designed to
demonstrate engineering capability. It is not connected to live financial
systems, does not execute trades, and does not determine legal insider-trading
intent.
