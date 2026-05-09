# IAM Module

Creates least-privilege IAM identities for QuantShield workloads and deployment automation.

## Roles and Policies

| Role | Trust policy | Permissions |
| --- | --- | --- |
| Lambda execution role | `lambda.amazonaws.com` | Creates Lambda log groups and writes log streams/events only for the configured Lambda function names. |
| EC2 instance role | `ec2.amazonaws.com` | Uses AWS Systems Manager core messaging APIs so instances can be managed without SSH credentials. AWS requires these SSM messaging actions to use `Resource = "*"`. |
| GitHub Actions deploy role | GitHub Actions OIDC provider | Deploys Terraform-managed QuantShield networking, EC2, IAM, and OIDC resources for the configured environment. The trust policy is restricted to the configured `owner/repo` and allowed refs. |

The deploy role intentionally avoids `AdministratorAccess`, `iam:*`, and `ec2:*`. Some EC2 describe and lifecycle actions require wildcard resources because AWS does not support resource-level constraints for those APIs.
