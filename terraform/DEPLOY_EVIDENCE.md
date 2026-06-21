# QuantShield IAM Sandbox Deploy Evidence

Date: 2026-06-21

Account IDs are redacted as `<ACCOUNT_ID>`.

## Scope

This evidence covers a targeted Terraform apply of `module.iam` only:

```powershell
terraform -chdir=terraform/environments/dev apply -auto-approve '-target=module.iam'
```

The full dev environment was not applied because it contains EC2 and RDS resources
that can create cost. The targeted IAM apply created only IAM resources and one
account-level AWS IAM Access Analyzer.

## Terraform Apply Result

```text
Apply complete! Resources: 13 added, 0 changed, 0 destroyed.

Outputs:

access_analyzer_arn = "arn:aws:access-analyzer:us-east-1:<ACCOUNT_ID>:analyzer/quantshield-dev-access-analyzer"
deploy_permission_boundary_arn = "arn:aws:iam::<ACCOUNT_ID>:policy/quantshield-dev-deploy-permission-boundary"
ec2_instance_profile_name = "quantshield-dev-ec2-profile"
ec2_role_arn = "arn:aws:iam::<ACCOUNT_ID>:role/quantshield-dev-ec2-role"
github_actions_deploy_role_arn = "arn:aws:iam::<ACCOUNT_ID>:role/quantshield-dev-github-actions-deploy"
github_oidc_provider_arn = "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
lambda_role_arn = "arn:aws:iam::<ACCOUNT_ID>:role/quantshield-dev-lambda-role"
```

## Access Analyzer Evidence

Command:

```powershell
aws accessanalyzer list-analyzers --type ACCOUNT
```

Redacted output:

```json
{
  "analyzers": [
    {
      "arn": "arn:aws:access-analyzer:us-east-1:<ACCOUNT_ID>:analyzer/quantshield-dev-access-analyzer",
      "name": "quantshield-dev-access-analyzer",
      "type": "ACCOUNT",
      "createdAt": "2026-06-21T19:29:05+00:00",
      "tags": {
        "Project": "quantshield",
        "Environment": "dev",
        "Owner": "Ryan",
        "ManagedBy": "Terraform",
        "Name": "quantshield-dev-access-analyzer"
      },
      "status": "ACTIVE"
    }
  ]
}
```

Command:

```powershell
aws accessanalyzer list-findings --analyzer-arn arn:aws:access-analyzer:us-east-1:<ACCOUNT_ID>:analyzer/quantshield-dev-access-analyzer
```

Result:

```json
{
  "findings": []
}
```

This is expected for a minimal sandbox account. It still validates that the
QuantShield pipeline can reach the live AWS IAM Access Analyzer API.

## Permission Boundary Evidence

Command:

```powershell
aws iam get-role --role-name quantshield-dev-github-actions-deploy
```

Redacted proof:

```json
{
  "Role": {
    "RoleName": "quantshield-dev-github-actions-deploy",
    "Arn": "arn:aws:iam::<ACCOUNT_ID>:role/quantshield-dev-github-actions-deploy",
    "AssumeRolePolicyDocument": {
      "Statement": [
        {
          "Principal": {
            "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
          },
          "Action": "sts:AssumeRoleWithWebIdentity",
          "Condition": {
            "StringEquals": {
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
            },
            "StringLike": {
              "token.actions.githubusercontent.com:sub": "repo:RyanMFurman/quantshield:ref:refs/heads/main"
            }
          }
        }
      ]
    },
    "PermissionsBoundary": {
      "PermissionsBoundaryType": "Policy",
      "PermissionsBoundaryArn": "arn:aws:iam::<ACCOUNT_ID>:policy/quantshield-dev-deploy-permission-boundary"
    }
  }
}
```

Command:

```powershell
aws iam list-attached-role-policies --role-name quantshield-dev-github-actions-deploy
```

Redacted proof:

```json
{
  "AttachedPolicies": [
    {
      "PolicyName": "quantshield-dev-github-actions-deploy",
      "PolicyArn": "arn:aws:iam::<ACCOUNT_ID>:policy/quantshield-dev-github-actions-deploy"
    }
  ]
}
```

## IAM Policy Linter

Command:

```powershell
.\.venv\Scripts\python.exe scripts\lint_iam_policies.py terraform
```

Output:

```text
IAM policy lint passed: no wildcard actions, AdministratorAccess, or mutating Resource '*' statements found.
```

## Terraform Validate

Command:

```powershell
terraform -chdir=terraform/environments/dev validate
```

Output:

```text
Success! The configuration is valid.
```

## Tests

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

Output:

```text
30 passed in 0.84s
```

## Cost Control

No EC2, RDS, NAT Gateway, ALB, or other paid compute/networking resources were
created in this evidence run. The targeted apply created IAM roles, IAM
policies, one GitHub OIDC provider, one instance profile, and one account-level
AWS IAM Access Analyzer. These resources have no expected ongoing hourly cost in
this sandbox setup.

The IAM sandbox resources were intentionally left in place after validation so
the Access Analyzer integration remains testable from the dashboard/API.
