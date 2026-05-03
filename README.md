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

### Dashboard & Visibility

- Streamlit operations dashboard
- Live alerts
- Compliance metrics
- Security telemetry views

### DevOps Workflow

- Protected `main` branch
- Feature branch development model
- Pull request approvals
- GitHub Actions CI/CD pipeline

---

## High-Level Architecture

```text
                    ┌────────────────────┐
                    │   Streamlit UI     │
                    │ FastAPI Backend    │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ PostgreSQL (RDS)   │
                    │ Alerts / Events    │
                    └─────────┬──────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ Market Ingest  │   │ Detection Eng. │   │ Incident Resp. │
│ Python / Lambda│   │ Rules Engine   │   │ Auto Actions   │
└────────────────┘   └────────────────┘   └────────────────┘
         ▲
         │
┌────────────────────────────────────────────┐
│ AWS Logs / CloudTrail / GuardDuty / Events │
└────────────────────────────────────────────┘

Technology Stack
Layer	Technology
Cloud	AWS
IaC	Terraform
Backend	Python / FastAPI
Database	PostgreSQL
Dashboard	Streamlit
Containers	Docker
CI/CD	GitHub Actions
Security	IAM / CloudTrail / GuardDuty
Current Progress
Completed
Terraform networking module
VPC + subnet + routing
Security groups
Apply / destroy tested
Branch protections enabled
Team workflow established
In Progress
IAM module
RDS PostgreSQL layer
API foundation
Detection engine
Planned
Streamlit dashboard
GuardDuty integrations
GitHub Actions pipelines
Public live deployment
Repository Structure
quantshield/
├── terraform/
│   ├── environments/
│   └── modules/
├── src/
│   ├── api/
│   ├── ingestion/
│   ├── detection/
│   └── response/
├── sql/
├── docs/
├── tests/
└── .github/workflows/
Engineering Workflow
1 Issue = 1 Branch = 1 Pull Request

Example:

feature/networking-module
feature/iam-module
feature/rds-module
feature/detection-engine

All changes require review before merge into main.

Security Principles
Least privilege IAM
No secrets committed
Protected main branch
Infrastructure version control
Controlled cloud deployments
Audit visibility through logs
Roadmap
 Networking Foundation
 IAM Architecture
 PostgreSQL Data Layer
 FastAPI Backend
 Detection Rules Engine
 Dashboard UI
 CI/CD Automation
 Public Demo Deployment
Author

Ryan Furman
Cloud / DevOps / Infrastructure Engineering

Collaborative project with security engineering contributions.

Disclaimer

QuantShield is a simulated educational and portfolio environment designed to demonstrate engineering capability. It is not connected to live financial systems. 