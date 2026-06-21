# QuantShield Portfolio Positioning

## Project One-Liner

QuantShield is a Dockerized IAM threat detection lab for a simulated quant
trading firm, with CloudTrail-style telemetry, identity-risk alerts,
insider-risk correlation, and analyst triage workflows.

## Honest Framing

This is not an "insider trading detector." That would be legally and
investigatively inaccurate.

The accurate framing is stronger:

> QuantShield detects identity abuse and sensitive research-data access that may
> create insider-risk exposure inside a simulated financial research
> environment.

That matches how a real SOC, cloud security team, or GRC-adjacent investigation
would treat the signal: the tool raises risk, then humans investigate intent,
policy violations, data exposure, and business context.

## Ryan Focus: AWS / IAM / Cloud Security Engineering

Use this version when Ryan wants the project to support IAM, cloud security, or
AWS platform roles:

> Built the AWS-oriented platform foundation for QuantShield, a Dockerized IAM
> threat detection lab for a simulated quant trading firm. Designed the
> local-to-AWS architecture, FastAPI service layer, PostgreSQL-backed telemetry
> model, Docker Compose demo stack, EC2/RDS/Nginx/HTTPS deployment runbooks, and
> IAM-focused project story mapping simulated CloudTrail events to real AWS
> security operations.

Skills shown:

- AWS architecture planning
- IAM threat modeling
- CloudTrail event understanding
- EC2 and RDS deployment design
- security group and private database access patterns
- Docker Compose operations
- FastAPI service design
- CI/testing discipline
- production-minded documentation

## Noah Focus: SOC / Detection Engineering

Use this version when Noah wants the project to support SOC analyst, detection
engineer, or cloud detection roles:

> Built the detection engineering core for QuantShield, including CloudTrail-style
> IAM scenarios, MITRE-mapped detection rules, alert deduplication, database
> detection cycles, P1 response hooks, API visibility, and tests for IAM abuse,
> brute force, privilege escalation, lateral movement, data exfiltration, and
> insider-risk correlation.

Skills shown:

- detection logic design
- alert severity modeling
- MITRE ATT&CK mapping
- CloudTrail-style event analysis
- SOC triage workflow thinking
- database-backed alert persistence
- unit testing of security logic

## 90-Second Demo Script

1. Open the dashboard and show the overview.
2. Explain the company story: a quant firm with AWS-hosted research data,
   trading-service accounts, IAM roles, and market telemetry.
3. Open the IAM Risk tab and show root login, MFA disablement, access key,
   admin-policy, and privileged-role alerts.
4. Open the Insider Risk tab and explain that QuantShield correlates
   symbol-specific S3 research-data access with unusual market context.
5. Open API docs or API endpoints to show this is not just a static dashboard.
6. Mention that it runs locally for reviewers, but the docs map it to EC2, RDS,
   CloudTrail, EventBridge, S3, IAM, Nginx, HTTPS, and GitHub Actions.

## Resume Bullets

Ryan:

- Built QuantShield, a Dockerized IAM threat detection lab for a simulated quant
  trading firm using Python, FastAPI, PostgreSQL, Streamlit, Docker, Terraform,
  and AWS-oriented deployment patterns.
- Designed the AWS demo architecture and runbooks for EC2, RDS PostgreSQL,
  security groups, IAM roles, Nginx, HTTPS, and scheduled telemetry refresh.
- Modeled CloudTrail-style IAM telemetry and API-backed SOC workflows for root
  activity, MFA disablement, access key creation, privilege escalation, and
  suspicious research-data access.

Noah:

- Implemented SOC detection engineering workflows for QuantShield, including
  MITRE-mapped IAM, brute-force, privilege-escalation, lateral-movement, and
  data-exfiltration detections.
- Built alert deduplication, database detection cycles, P1 response hooks, and
  tests for CloudTrail-style security telemetry and insider-risk correlation.

## What Makes It Stand Out

Most beginner cloud projects are CRUD apps, static dashboards, or basic stock
screeners. QuantShield is more specific:

- It has a believable company environment.
- It focuses on IAM, which is a real AWS security hiring lane.
- It combines cloud telemetry, market context, data access, detection logic, and
  analyst workflow.
- It can run locally for free while still telling a credible AWS deployment
  story.

## What To Say In Interviews

Say:

- "This is a simulated IAM threat detection lab."
- "The insider-risk part is correlation, not a legal conclusion."
- "The AWS version would replace simulated events with CloudTrail/EventBridge
  ingestion."
- "The local version exists so any reviewer can run it without an AWS bill."
- "My focus was AWS/IAM/platform reliability; Noah's focus was detection/SOC
  logic."

Avoid saying:

- "It detects insider trading."
- "It is production-ready for a real financial institution."
- "It connects to live trading systems."
- "It proves user intent."
