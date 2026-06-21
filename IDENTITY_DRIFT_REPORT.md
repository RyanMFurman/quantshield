# IdentityDrift Report

Generated: 2026-06-21T20:16:37.434453+00:00
Source: sample-data

## Summary

- AWS-granting Okta users reviewed: 2
- AWS permission sets reviewed: 3
- Stale AWS access findings: 1
- Unused permission set findings: 2

## Stale AWS Access Findings

| User | Groups | Okta Last Login | AWS Last Used | Reason |
|---|---|---:|---:|---|
| stale.readonly@example.com | AWS-ReadOnly | 365 days ago | never observed | User is in an AWS-granting Okta group but has no observed AWS usage. |

## Unused Permission Sets

| Permission Set | Groups | Assigned Users | Reason |
|---|---|---:|---|
| IdentityDrift-ReadOnly | AWS-ReadOnly | 1 | Permission set has assigned users but no observed AWS usage. |
| IdentityDrift-Billing | AWS-Billing | 0 | Permission set has no assigned Okta users through its mapped groups. |

## Analyst Notes

- A finding means access should be reviewed; it does not prove misuse.
- Users with no observed AWS use are strong candidates for group removal or permission set review.
- Permission sets with zero usage should be validated with the business owner before removal.
