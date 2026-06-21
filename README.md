# QuantShield

![Status](https://img.shields.io/badge/status-active_development-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![AWS](https://img.shields.io/badge/cloud-AWS-orange)
![Python](https://img.shields.io/badge/backend-Python-yellow)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![License](https://img.shields.io/badge/license-MIT-green)

AWS IAM threat detection and least-privilege lab for a simulated quant trading
firm, built with Terraform, IAM Access Analyzer, Python, PostgreSQL, FastAPI,
Streamlit, Docker, and GitHub Actions.

## Live Demo

Public demo URLs:

- Dashboard: `https://demo.example.com`
- API health: `https://api.example.com/health`
- Insider risk API: `https://api.example.com/api/v1/insider-risk`

Replace the example domains after the AWS host, DNS, and HTTPS setup are complete.

## What This Project Does

QuantShield is an IAM-focused cloud security lab. It combines Terraform-managed
AWS IAM controls, a live AWS IAM Access Analyzer integration, permission drift
analysis, policy linting, CloudTrail-style detection rules, and a Dockerized
analyst dashboard.

The IAM-specific capabilities come first:

- AWS IAM Access Analyzer account-level analyzer in Terraform
- API and dashboard ingestion path for live Access Analyzer findings
- permission drift reporting that compares granted IAM actions against observed usage
- CI IAM policy linting for wildcard actions, broad resources, and administrator access
- permission boundary on the GitHub Actions deploy role
- OIDC federation for GitHub Actions instead of static AWS keys

The simulated SOC layer then models high-value identity and data-access risks
that matter in financial research environments:

- IAM privilege escalation
- access key creation
- root account activity
- MFA disablement
- privileged role assumption
- S3 research-data access
- abnormal market-data context around sensitive activity

The full-incident demo story:

> A simulated quant analyst account creates an access key, assumes a privileged trading role, attaches administrative access, touches NVDA research data in S3, and disables MFA. QuantShield correlates the IAM telemetry with abnormal NVDA market movement and raises identity-risk and insider-risk alerts for analyst triage.

For false-positive testing, the default scenario is `quiet_day`, not the dramatic
incident path.

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
- Docker Compose lab that runs PostgreSQL, FastAPI, Streamlit, schema setup, and
  repeatable demo seeding with service healthchecks and no AWS spend required
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
  - Root cloud account login (`T1078.004`)
  - MFA device disabled (`T1556.006`)
  - Access key creation (`T1098.001`)
  - Cloud policy modification (`T1484.002`)
  - Privileged cloud role assumption (`T1078.004`)
  - Cloud role hopping / multi-host access (`T1078.004`)
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

- IAM Access Analyzer ingestion path for live AWS account findings
- Least-privilege permission drift reporting from Terraform policies vs observed usage
- CI-enforced IAM policy linting for wildcard actions, broad resources, and administrator access
- Permission boundary on the GitHub Actions deploy role to reduce IAM escalation risk
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

## IAM Engineering Capabilities

### Access Analyzer Integration

QuantShield includes an optional AWS IAM Access Analyzer ingestion path. Set
`ACCESS_ANALYZER_ARN` and `AWS_REGION` to query a real account-level analyzer and
show active findings in the dashboard. In a minimal sandbox account this may
return zero findings, which is expected and still validates the live AWS pipeline
without creating paid workloads.

### Permission Drift Detection

The permission drift report compares IAM actions granted in
`terraform/modules/iam` with IAM-style actions observed in recent
CloudTrail-style telemetry. Roles with no usage data are reported as
`No usage data` instead of misleadingly showing 100% drift.

### IAM Policy Linting

CI runs `scripts/lint_iam_policies.py terraform` against Terraform IAM policy
documents. The check fails on wildcard actions, `AdministratorAccess`, or
mutating actions paired with `Resource = "*"`. Current result:

```text
IAM policy lint passed: no wildcard actions, AdministratorAccess, or mutating Resource '*' statements found.
```

### Permission Boundary

The Terraform IAM module attaches a permission boundary to the GitHub Actions
deploy role. The boundary denies IAM actions outside QuantShield-prefixed roles,
policies, and instance profiles; denies human user/access-key creation; and
blocks the deploy role from removing or replacing its own boundary.

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
- `GET /api/v1/access-analyzer/findings`
- `GET /api/v1/permission-drift`

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

Refresh demo data manually. The default is `quiet_day`; use `full_incident` for
the worst-case demo path:

```bash
docker compose run --rm demo-seed --scenario quiet_day
docker compose run --rm demo-seed --scenario full_incident
```

## Detection Engine Quickstart

Run local demo scenarios (no DB required):

```bash
python3 scripts/run_detection_demo.py --scenario quiet_day
python3 scripts/run_detection_demo.py --scenario noisy_benign
python3 scripts/run_detection_demo.py --scenario p2_only
python3 scripts/run_detection_demo.py --scenario full_incident
```

Run detection engine DB cycle (requires `DATABASE_URL`):

```bash
python3 scripts/run_detection_db_cycle.py
```

Run insider-risk analysis DB cycle (requires `DATABASE_URL`):

```bash
python3 scripts/run_insider_risk_analysis.py
```

Seed a scenario and run both detection cycles (requires `DATABASE_URL`):

```bash
python3 scripts/seed_live_demo_data.py --scenario quiet_day
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
python3 -m pytest -q tests
python3 scripts/lint_iam_policies.py terraform
terraform -chdir=terraform/environments/dev validate
```

## Live Demo Deployment

See `docs/live-demo-aws.md` for the EC2, Docker Compose, Nginx, and RDS-backed
demo runbook. See `docs/live-rds-app-config.md` for live database and app
environment configuration.

See `terraform/DEPLOY_EVIDENCE.md` for redacted evidence from a targeted live
AWS IAM module apply. That evidence created IAM roles/policies, a GitHub OIDC
provider, a permission boundary, and an account-level IAM Access Analyzer. The
full EC2/RDS stack was intentionally not applied during that evidence run to
control cost.

## Security Engineering Decisions

### OIDC Instead of Static AWS Keys

GitHub Actions is designed to assume an AWS role through OIDC federation. That
avoids long-lived AWS access keys in GitHub secrets and restricts role assumption
to `RyanMFurman/quantshield` on configured refs.

### Scoped Deploy Role Permissions

The deploy role uses customer-managed policies instead of broad AWS managed
policies. IAM resources are scoped to the `quantshield-dev-*` prefix, and EC2
permissions are read-only describe actions. This keeps automation useful for
validation without giving it account-wide infrastructure mutation rights.

### Permission Boundary

The deploy role has a permission boundary because it is the most sensitive
automation identity in the project. The boundary prevents self-escalation by
denying IAM actions outside QuantShield-prefixed resources, denying user/access
key creation, and blocking boundary removal from the deploy role.

### Permission Drift Detector

The drift detector compares Terraform-granted IAM actions with observed
CloudTrail-style usage. It identifies granted-but-unused permissions and returns
a recommended action removal list. Roles with no telemetry are marked as no
usage data instead of being misreported as 100% drift.

### Access Analyzer Findings

The live sandbox Access Analyzer returned zero active findings, which is
expected for a minimal account. The important proof is that the analyzer exists,
is ACTIVE, and QuantShield can query the AWS Access Analyzer API path without
creating paid workloads.

## Portfolio Summary

Built a Dockerized IAM threat detection lab for a simulated quant trading firm
using AWS-oriented architecture, Terraform, Python, PostgreSQL, FastAPI, Docker,
and Streamlit to simulate CloudTrail-style telemetry, identity-risk alerts,
insider-risk correlation, and analyst triage workflows.

## Completed Capabilities

- Local Docker SOC lab with PostgreSQL, FastAPI, Streamlit, schema setup,
  service healthchecks, and repeatable demo data
- Live IAM Access Analyzer integration path and redacted AWS deploy evidence
- Permission drift detector for Terraform IAM policies vs observed usage
- CI-enforced IAM policy linting
- Permission boundary on the GitHub Actions deploy role
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
