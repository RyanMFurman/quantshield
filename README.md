# QuantShield

![Status](https://img.shields.io/badge/status-active_development-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![AWS](https://img.shields.io/badge/cloud-AWS-orange)
![Python](https://img.shields.io/badge/backend-Python-yellow)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Cloud-Native Financial Security Operations Platform built with AWS, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

QuantShield simulates the cloud infrastructure and security operations center of a boutique quantitative trading firm. The platform combines real AWS infrastructure, security telemetry, threat detection, automated response workflows, and operational dashboards into a production-style engineering project.

---

## Why This Project Exists

QuantShield was built to demonstrate real-world skills across:

- Cloud Infrastructure Engineering
- DevOps / Infrastructure as Code
- AWS Security Operations
- Python Backend Development
- CI/CD Automation
- Threat Detection Engineering
- Systems Architecture

This is not a tutorial CRUD app. It is a full-stack cloud security platform designed as a recruiter-visible portfolio project.

---

## Core Features

### Infrastructure as Code

- AWS infrastructure fully managed with Terraform
- Modular environments (`dev`, `prod`)
- Reproducible deployments
- Version-controlled infrastructure

### Cloud Security Monitoring

- Synthetic AWS security event generation
- CloudTrail / GuardDuty integrations
- IAM monitoring
- Detection rules mapped to MITRE ATT&CK

### Backend & Data Platform

- FastAPI REST API
- PostgreSQL relational datastore
- Python ingestion pipelines
- Alert + incident tracking
- API skeleton exposes `/health`, `/market/latest`, and `/alerts/active`

### Dashboard & Visibility

- Streamlit operations dashboard
- Live alerts
- Compliance metrics
- Security telemetry views
- Skeleton dashboard consumes FastAPI endpoints with graceful empty states

### DevOps Workflow

- Protected `main` branch
- Feature branch development model
- Pull request approvals
- GitHub Actions CI/CD pipeline
- Python API smoke tests and Terraform validation workflows

---

## High-Level Architecture

```text
                    +--------------------+
                    |    Streamlit UI    |
                    |  FastAPI Backend   |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | PostgreSQL (RDS)   |
                    | Alerts / Events    |
                    +---------+----------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
+----------------+  +----------------+  +----------------+
| Market Ingest  |  | Detection Eng. |  | Incident Resp. |
| Python/Lambda  |  | Rules Engine   |  | Auto Actions   |
+----------------+  +----------------+  +----------------+
          ^
          |
+----------------------------------------------+
| AWS Logs / CloudTrail / GuardDuty / Events   |
+----------------------------------------------+
```

## Technology Stack

| Layer | Technology |
| --- | --- |
| Cloud | AWS |
| IaC | Terraform |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Dashboard | Streamlit |
| Containers | Docker |
| CI/CD | GitHub Actions |
| Security | IAM / CloudTrail / GuardDuty |

## API Quickstart

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the FastAPI app:

```powershell
uvicorn src.api.main:app --reload
```

Available routes:

- `GET /health`
- `GET /market/latest`
- `GET /alerts/active`

Run the Streamlit dashboard:

```powershell
streamlit run src/api/dashboard.py
```

Set `DATABASE_URL` to query PostgreSQL-backed routes. Without it, data routes return empty results with `database_configured = false`.
Set `QUANTSHIELD_API_URL` if the Streamlit dashboard should point at a non-local FastAPI service.

## Current Progress

### Completed

- Terraform networking module
- VPC, subnet, routing, and security groups
- Apply and destroy tested
- Branch protections enabled
- Team workflow established
- PostgreSQL data layer
- RDS PostgreSQL provisioned with Terraform
- Schema initialization verified against AWS RDS
- Seed data loaded and verified in `security_events`
- FastAPI backend skeleton
- Health, market latest, and active alerts routes
- Streamlit dashboard skeleton
- GitHub Actions Python and Terraform validation workflows

### In Progress

- IAM module
- Detection engine

### Planned

- GuardDuty integrations
- Public live deployment

## Repository Structure

```text
quantshield/
  .github/workflows/
  terraform/
  src/
  sql/
  docs/
  tests/
```

## Engineering Workflow

1 Issue = 1 Branch = 1 Pull Request

Example:

```text
feature/networking-module
feature/iam-module
feature/rds-module
feature/detection-engine
```

All changes require review before merge into `main`.

## Security Principles

- Least privilege IAM
- No secrets committed
- Protected main branch
- Infrastructure version control
- Controlled cloud deployments
- Audit visibility through logs

## Roadmap

- Networking Foundation
- IAM Architecture
- PostgreSQL Data Layer
- FastAPI Backend
- Detection Rules Engine
- Dashboard UI
- CI/CD Automation
- Public Demo Deployment

## Author

Ryan Furman  
Cloud / DevOps / Infrastructure Engineering

Collaborative project with security engineering contributions.

## Disclaimer

QuantShield is a simulated educational and portfolio environment designed to demonstrate engineering capability. It is not connected to live financial systems.
