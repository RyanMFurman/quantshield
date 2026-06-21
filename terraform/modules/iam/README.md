# IAM Module

Creates least-privilege IAM identities for QuantShield workloads and deployment automation.

## Roles and Policies

| Role | Trust policy | Permissions |
| --- | --- | --- |
| Lambda execution role | `lambda.amazonaws.com` | Creates Lambda log groups and writes log streams/events only for the configured Lambda function names. |
| EC2 instance role | `ec2.amazonaws.com` | Uses AWS Systems Manager core messaging APIs so instances can be managed without SSH credentials. AWS requires these SSM messaging actions to use `Resource = "*"`. |
| GitHub Actions deploy role | GitHub Actions OIDC provider | Manages QuantShield-prefixed IAM resources and the account-level Access Analyzer for the configured environment. The trust policy is restricted to the configured `owner/repo` and allowed refs. |

The deploy role intentionally avoids `AdministratorAccess`, `iam:*`, and `ec2:*`. EC2 access is read-only describe access so CI can inspect infrastructure without mutating compute or networking.

## Access Analyzer

The module creates an account-level `aws_accessanalyzer_analyzer`. IAM Access Analyzer analyzers are free for standard external-access analysis and let the project validate a live AWS IAM finding-ingestion path even in a low-cost sandbox account.

## Permission Boundary

The GitHub Actions deploy role has a permission boundary to prevent privilege escalation through self-modifying IAM. The boundary denies IAM actions outside QuantShield-prefixed roles, policies, and instance profiles, explicitly denies human user/access-key creation, and blocks changing the deploy role's own boundary. This keeps the most privileged automation role scoped to the project instead of becoming a path to broader account administration.
