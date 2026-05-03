# QuantShield

QuantShield is a cloud-native financial SOC platform using AWS, Terraform, Python, PostgreSQL, FastAPI, Streamlit, Docker, and GitHub Actions.

## Terraform Dev Networking

The dev Terraform environment provisions the initial AWS networking foundation in `us-east-1`: a VPC, one public subnet, an internet gateway, public routing, and an EC2 security group for web traffic plus SSH from `admin_cidr`.

From `terraform/environments/dev`, run:

```bash
terraform init
terraform validate
terraform plan
```

Use `terraform.tfvars.example` as a safe template for local values. Do not commit real `terraform.tfvars`, secrets, AWS credentials, state files, or generated Terraform directories.
