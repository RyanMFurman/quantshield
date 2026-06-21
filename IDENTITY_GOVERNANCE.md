# IdentityDrift: Okta-to-AWS Federated Identity Governance

IdentityDrift is a focused IAM governance extension for QuantShield. The goal is
to prove access lifecycle control and least-privilege review across an external
identity provider and AWS IAM Identity Center, not just inside one AWS account.

## Scope

In scope:

- Okta free developer org as the identity provider.
- AWS IAM Identity Center in a single AWS account.
- SAML 2.0 federation from Okta to IAM Identity Center.
- Okta groups mapped to AWS permission sets.
- SCIM provisioning from Okta to IAM Identity Center.
- MFA required in Okta for AWS access.
- Markdown drift report for stale AWS-granting users and unused permission sets.

Out of scope for this pass:

- AWS Organizations or multi-account governance.
- Control Tower.
- New Streamlit dashboard.
- Slack, SNS, email, or ticketing alerts.

## Phase 1: Okta and AWS Federation Setup

Status: documented operator steps. These console steps must be performed manually
in the Okta developer org and AWS console. They were not executed by Codex.

### 1. Create Okta Free Developer Org

1. Go to `https://developer.okta.com/signup/`.
2. Sign up for a free Okta developer organization.
3. Verify email and sign in to the Okta Admin Console.
4. Save the Okta org URL for later:

```text
https://<your-okta-domain>.okta.com
```

5. In Okta Admin Console, go to `Security > API`.
6. Open `Tokens`.
7. Click `Create token`.
8. Name the token:

```text
identitydrift-dev-token
```

9. Copy the token once and store it locally as an environment variable:

```powershell
$env:OKTA_ORG_URL="https://<your-okta-domain>.okta.com"
$env:OKTA_API_TOKEN="<redacted>"
```

Do not commit the token.

### 2. Enable AWS IAM Identity Center

1. Open AWS Console.
2. Search for `IAM Identity Center`.
3. Open `IAM Identity Center`.
4. If not enabled, click `Enable`.
5. Choose the current AWS account as the management location.
6. Stay in single-account mode. AWS Organizations and Control Tower are out of
   scope for this pass.
7. In the left navigation, open `Settings`.
8. Record these values for the SAML setup:

```text
AWS access portal URL: https://<generated>.awsapps.com/start
IAM Identity Center region: <region>
```

### 3. Create Okta AWS IAM Identity Center SAML App

Use the built-in Okta AWS IAM Identity Center app integration when available.

1. In Okta Admin Console, go to `Applications > Applications`.
2. Click `Browse App Catalog`.
3. Search for:

```text
AWS IAM Identity Center
```

4. Add the app integration.
5. Name the app:

```text
AWS IAM Identity Center - IdentityDrift
```

6. In the Okta app, open the `Sign On` tab.
7. Download or copy the Okta IdP metadata:

```text
Identity Provider metadata URL
```

or download:

```text
metadata.xml
```

8. Keep the Okta app open. AWS metadata from IAM Identity Center will be added
   after AWS is switched to external identity provider mode.

### 4. Switch IAM Identity Center Identity Source to External IdP

1. In AWS IAM Identity Center, open `Settings`.
2. Under `Identity source`, click `Actions`.
3. Choose `Change identity source`.
4. Select:

```text
External identity provider
```

5. Download the AWS IAM Identity Center service provider metadata file.
6. Upload the Okta IdP metadata file or paste the Okta metadata URL into AWS.
7. Confirm the identity source change.

Expected AWS result:

```text
Identity source: External identity provider
Authentication method: SAML 2.0
```

### 5. Finish Okta SAML Configuration

1. Return to the Okta app created in step 3.
2. Open the app `Sign On` settings.
3. Upload or paste AWS IAM Identity Center service provider metadata.
4. Confirm the SAML endpoints are populated from AWS metadata.
5. Save the app.

Expected Okta result:

```text
Application: AWS IAM Identity Center - IdentityDrift
Sign-on mode: SAML 2.0
```

### 6. Smoke Test SAML Login

This is only a federation smoke test. Permission sets and SCIM are configured in
later phases.

1. Assign your Okta test user directly to the AWS IAM Identity Center app.
2. Open the Okta end-user dashboard.
3. Click the AWS IAM Identity Center app tile.
4. Confirm redirect to the AWS access portal.

Expected result at this phase:

```text
Login succeeds, but AWS account access may be empty until permission sets and
assignments are configured.
```

## Screenshot Checklist

Save screenshots under:

```text
docs/screenshots/identitydrift/
```

Phase 1 screenshots to capture manually:

- `01-okta-dev-org-dashboard.png` - Okta Admin Console home page.
- `02-okta-aws-iam-identity-center-app.png` - Okta AWS IAM Identity Center app page.
- `03-okta-saml-sign-on-settings.png` - Okta SAML sign-on settings with sensitive values redacted.
- `04-aws-identity-center-enabled.png` - AWS IAM Identity Center settings page.
- `05-aws-external-idp-configured.png` - IAM Identity Center identity source showing external IdP.

## Reality Check

Phase 1 is not complete until the console screenshots above are captured. The
repository documentation now defines the exact setup path, but live federation is
not proven until manual console setup and screenshots are added.

## Phase 2: SCIM, Groups, Permission Sets, and MFA

Status: documented operator steps. These console steps must be performed manually
after Phase 1 SAML federation is working.

### 1. Create Okta Groups

In Okta Admin Console:

1. Go to `Directory > Groups`.
2. Click `Add group`.
3. Create these groups:

```text
AWS-Admins
AWS-ReadOnly
AWS-Billing
```

4. Add test users to the groups. Recommended test layout:

```text
AWS-Admins   -> one admin test user
AWS-ReadOnly -> one read-only test user
AWS-Billing  -> one billing test user
```

Do not use broad assignment like `Everyone` for AWS access. The point of this
lab is group-driven least privilege.

### 2. Create AWS IAM Identity Center Permission Sets

In AWS IAM Identity Center:

1. Go to `Permission sets`.
2. Click `Create permission set`.
3. Create these permission sets.

#### IdentityDrift-Admin

Use this only for the admin test group. Prefer a scoped custom policy instead of
AWS managed `AdministratorAccess`.

Recommended lab policy scope:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:Get*",
        "iam:List*",
        "iam:SimulatePrincipalPolicy",
        "access-analyzer:Get*",
        "access-analyzer:List*",
        "cloudtrail:LookupEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

This is intentionally not full administrator access. It supports IAM/security
review tasks while avoiding infrastructure mutation.

#### IdentityDrift-ReadOnly

Use AWS managed policy:

```text
ReadOnlyAccess
```

This is acceptable for the lab because the purpose is cross-account console
visibility without write access.

#### IdentityDrift-Billing

Use a custom billing-view policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "account:GetAccountInformation",
        "billing:Get*",
        "budgets:ViewBudget",
        "ce:Get*",
        "cur:Describe*",
        "payments:Get*",
        "tax:Get*"
      ],
      "Resource": "*"
    }
  ]
}
```

Billing APIs often require `Resource = "*"`. Keep this permission set read-only.

### 3. Assign Okta Groups to AWS Permission Sets

In AWS IAM Identity Center:

1. Go to `AWS accounts`.
2. Select the target sandbox account.
3. Click `Assign users or groups`.
4. Assign:

```text
AWS-Admins   -> IdentityDrift-Admin
AWS-ReadOnly -> IdentityDrift-ReadOnly
AWS-Billing  -> IdentityDrift-Billing
```

Expected outcome:

```text
Okta group membership controls AWS account access through IAM Identity Center
permission sets.
```

### 4. Enable SCIM Provisioning from Okta

Use the built-in Okta provisioning integration. Do not hand-roll SCIM.

In AWS IAM Identity Center:

1. Open `Settings`.
2. Go to `Automatic provisioning`.
3. Click `Enable`.
4. Copy:

```text
SCIM endpoint
Access token
```

In Okta Admin Console:

1. Open the `AWS IAM Identity Center - IdentityDrift` app.
2. Go to `Provisioning`.
3. Click `Configure API Integration`.
4. Check `Enable API integration`.
5. Paste the AWS IAM Identity Center SCIM endpoint.
6. Paste the SCIM access token.
7. Click `Test API Credentials`.
8. Save.
9. Under `To App`, enable:

```text
Create Users
Update User Attributes
Deactivate Users
Push Groups
```

10. Push these groups:

```text
AWS-Admins
AWS-ReadOnly
AWS-Billing
```

What SCIM actually does:

- Creates Okta users in IAM Identity Center.
- Updates user attributes in IAM Identity Center.
- Deactivates users in IAM Identity Center when removed/deactivated in Okta.
- Pushes selected Okta groups and group membership into IAM Identity Center.

What SCIM does not do:

- It does not create AWS IAM users.
- It does not create long-lived AWS access keys.
- It does not automatically design least-privilege policies.
- It does not replace permission set assignment review.

### 5. Require MFA for AWS Access in Okta

In Okta Admin Console:

1. Go to `Security > Authenticators`.
2. Ensure at least one strong factor is enabled, such as Okta Verify or WebAuthn.
3. Go to `Security > Global Session Policy` or `Security > Authentication Policies`
   depending on the Okta console version.
4. Create or edit a policy for AWS access.
5. Scope the policy to the AWS app or the AWS-granting groups:

```text
AWS-Admins
AWS-ReadOnly
AWS-Billing
```

6. Require MFA when accessing the AWS IAM Identity Center app.
7. Save the policy.

Expected outcome:

```text
Any user in an AWS-granting Okta group must satisfy MFA before reaching AWS.
```

### 6. Phase 2 Validation

After setup:

1. Add a user to `AWS-ReadOnly` in Okta.
2. Confirm SCIM creates/syncs the user in IAM Identity Center.
3. Confirm the user appears in the assigned AWS account with
   `IdentityDrift-ReadOnly`.
4. Remove the user from `AWS-ReadOnly`.
5. Confirm SCIM removes that group relationship from IAM Identity Center.

Expected result:

```text
Okta group changes sync into IAM Identity Center without manual AWS user work.
```

### Phase 2 Screenshot Checklist

Save screenshots under:

```text
docs/screenshots/identitydrift/
```

- `06-okta-aws-groups.png` - Okta groups `AWS-Admins`, `AWS-ReadOnly`, `AWS-Billing`.
- `07-aws-permission-sets.png` - IAM Identity Center permission sets.
- `08-aws-account-assignments.png` - AWS account assignments showing groups mapped to permission sets.
- `09-aws-scim-automatic-provisioning.png` - IAM Identity Center automatic provisioning enabled.
- `10-okta-scim-api-integration.png` - Okta provisioning API integration with secrets redacted.
- `11-okta-pushed-groups.png` - Okta pushed groups for AWS access.
- `12-okta-mfa-policy.png` - Okta MFA policy scoped to AWS app or AWS groups.

## Phase 2 Reality Check

Phase 2 is complete only after screenshots prove the Okta groups, SCIM
provisioning, permission sets, group assignments, and MFA policy exist. The repo
documents the exact steps, but Codex did not perform these browser console
actions.

## Phase 3: Drift Detection Code and Tests

Status: implemented and tested locally.

IdentityDrift adds a small Python governance pipeline instead of another
dashboard:

- `src/identity/okta_client.py` pulls Okta AWS-granting group membership and
  user last-login timestamps from the Okta API.
- `src/identity/aws_usage.py` models AWS permission set usage and can normalize
  IAM Access Analyzer unused-access findings.
- `src/identity/drift_report.py` cross-references Okta membership with AWS usage
  and renders a markdown report.
- `scripts/run_drift_report.py` is the CLI entrypoint.
- `tests/test_drift_report.py` covers stale users, active users, empty permission
  sets, markdown rendering, and Access Analyzer normalization.

### Run Offline with Sample Data

Use this when Okta/AWS federation is not configured yet:

```powershell
.\.venv\Scripts\python.exe scripts\run_drift_report.py --sample-data --output IDENTITY_DRIFT_REPORT.md
```

Sample output from the local run:

```text
AWS-granting Okta users reviewed: 2
AWS permission sets reviewed: 3
Stale AWS access findings: 1
Unused permission set findings: 2
```

Example sample finding:

```text
stale.readonly@example.com is in AWS-ReadOnly but has no observed AWS usage.
```

This is sample data, not a claim that a real Okta user was stale.

### Run Against Okta and AWS

After manual federation setup is complete:

```powershell
$env:OKTA_ORG_URL="https://<your-okta-domain>.okta.com"
$env:OKTA_API_TOKEN="<redacted>"
$env:OKTA_AWS_GROUPS="AWS-Admins,AWS-ReadOnly,AWS-Billing"
$env:ACCESS_ANALYZER_ARN="arn:aws:access-analyzer:<region>:<account-id>:analyzer/<name>"
$env:AWS_REGION="<region>"

.\.venv\Scripts\python.exe scripts\run_drift_report.py --days 30 --output IDENTITY_DRIFT_REPORT.md
```

If `ACCESS_ANALYZER_ARN` is set, the script queries IAM Access Analyzer and
normalizes unused-access findings into the permission set usage model. If the
sandbox has no unused-access findings, that is acceptable; the point is proving
the pipeline can call a real AWS IAM governance service without deploying paid
workloads.

### Phase 3 Test Proof

Local test command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_drift_report.py
```

Passing output:

```text
.....                                                                    [100%]
5 passed in 0.09s
```

Full repo test command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Passing output:

```text
..................................                                       [100%]
34 passed in 1.59s
```

## Phase 4: Final Report and Screenshot List

Status: report workflow implemented; live screenshots must be captured manually
after the Okta and AWS console setup is completed.

### What Was Federated

The target architecture federates Okta into AWS IAM Identity Center using SAML
2.0. Okta is the identity provider. IAM Identity Center is the AWS access
broker. Okta groups grant access to AWS permission sets:

```text
AWS-Admins   -> IdentityDrift-Admin
AWS-ReadOnly -> IdentityDrift-ReadOnly
AWS-Billing  -> IdentityDrift-Billing
```

No AWS IAM users or long-lived AWS access keys are created for people. Human
access flows through Okta, MFA, SAML, IAM Identity Center, and short-lived AWS
federated sessions.

### What SCIM Sync Actually Does

SCIM keeps IAM Identity Center aligned with Okta lifecycle state. When users are
added to, removed from, updated in, or deactivated from the pushed Okta groups,
those identity and group changes sync into IAM Identity Center.

SCIM does not replace access review. IdentityDrift exists because synced access
can still drift over time: users can remain in AWS-granting groups long after
they stop using AWS, and permission sets can stay assigned even when no one uses
them.

### Drift Finding Example

The local sample run produced this finding:

```text
stale.readonly@example.com | AWS-ReadOnly | AWS Last Used: never observed
Reason: User is in an AWS-granting Okta group but has no observed AWS usage.
```

For a live run, replace the sample report with one generated after Okta and IAM
Identity Center are connected:

```powershell
.\.venv\Scripts\python.exe scripts\run_drift_report.py --days 30 --output IDENTITY_DRIFT_REPORT.md
```

If a live run returns no findings, document it as:

```text
Ran clean: all AWS-granting Okta users had recent observed access, and no
permission sets showed zero usage in the available Access Analyzer data.
```

### Screenshot Checklist

Save screenshots under:

```text
docs/screenshots/identitydrift/
```

Required final screenshots:

- `13-okta-user-in-aws-readonly-group.png` - Okta user assigned to an AWS-granting group.
- `14-aws-identity-center-synced-users.png` - IAM Identity Center users synced from Okta.
- `15-aws-identity-center-synced-groups.png` - IAM Identity Center groups synced from Okta.
- `16-aws-permission-set-assignment-detail.png` - AWS account assignment showing group-to-permission-set mapping.
- `17-access-analyzer-analyzer-or-findings.png` - IAM Access Analyzer analyzer or findings page.
- `18-identitydrift-cli-run.png` - Terminal showing `scripts/run_drift_report.py` completed.
- `19-identitydrift-report-output.png` - Open `IDENTITY_DRIFT_REPORT.md` showing findings or clean run.

### Real vs. Not Yet Live

Real and tested in this repo:

- Okta API client structure for group membership and last-login collection.
- AWS usage model and IAM Access Analyzer unused-access normalization.
- Markdown drift report generation.
- CLI runner with deterministic sample mode.
- Unit tests for stale user detection, active user handling, empty permission set
  handling, report rendering, and Access Analyzer finding normalization.
- Full local test suite passing.

Not live until you complete the console work:

- Okta developer org creation.
- SAML federation into IAM Identity Center.
- SCIM provisioning.
- Okta MFA enforcement.
- Live Okta API pull using your real `OKTA_API_TOKEN`.
- Live Access Analyzer pull using your real `ACCESS_ANALYZER_ARN`.

Free-tier limitation:

- IAM Identity Center, IAM roles, Okta developer org testing, and account-level
  IAM Access Analyzer can be used without deploying paid workloads.
- Access Analyzer may return no findings in a clean sandbox account. That is not
  a failure; it proves the pipeline can validate against a low-cost AWS
  governance service while keeping the lab controlled.
