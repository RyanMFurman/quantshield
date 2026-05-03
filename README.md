# QuantShield

QuantShield is a cloud-native financial SOC platform using AWS, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

## Terraform Dev Networking

The dev Terraform environment provisions the initial AWS networking foundation in `us-east-1`: a VPC, one public subnet, an internet gateway, public routing, and an EC2 security group for web traffic plus SSH from `admin_cidr`.

The dev environment also includes a small temporary EC2 web test instance so the public subnet, route table, internet gateway, and security group can be verified end to end.

Security group rules:

- Inbound HTTP `80` from `0.0.0.0/0`
- Inbound HTTPS `443` from `0.0.0.0/0`
- Inbound SSH `22` only from `admin_cidr`
- Outbound traffic to `0.0.0.0/0`

From `terraform/environments/dev`, run:

```bash
terraform init
terraform validate
terraform plan
```

To temporarily verify the stack in AWS, use safe local values based on `terraform.tfvars.example`, then run:

```bash
terraform apply
terraform output web_test_url
terraform destroy
```

Use `terraform.tfvars.example` as a safe template for local values. Do not commit real `terraform.tfvars`, secrets, AWS credentials, state files, or generated Terraform directories.
