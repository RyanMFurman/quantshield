locals {
  name_prefix      = "${var.project_name}-${var.environment}"
  schema_file_path = var.schema_file_path != null ? var.schema_file_path : abspath("${path.root}/../../../sql/schema.sql")
  seed_file_path   = var.seed_file_path != null ? var.seed_file_path : abspath("${path.root}/../../../sql/seed_data.sql")
}

# Security group keeps PostgreSQL reachable for issue #3 validation while limiting
# access to the trusted CIDRs passed by the environment, normally admin_cidr in dev.
resource "aws_security_group" "postgres" {
  name        = "${local.name_prefix}-postgres-sg"
  description = "Allow PostgreSQL access from trusted CIDR blocks"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL from trusted CIDR blocks"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-postgres-sg"
  })
}

resource "aws_db_subnet_group" "this" {
  name        = "${local.name_prefix}-postgres-subnets"
  description = "Subnet group for ${local.name_prefix} PostgreSQL"
  subnet_ids  = var.subnet_ids

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-postgres-subnets"
  })
}

# RDS hosts the PostgreSQL database. AWS manages the master password in Secrets
# Manager, so Terraform never needs to store a plaintext database credential.
resource "aws_db_instance" "this" {
  identifier = "${local.name_prefix}-postgres"

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_encrypted     = true
  storage_type          = "gp3"

  db_name  = var.database_name
  username = var.master_username

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.postgres.id]
  publicly_accessible    = var.publicly_accessible

  backup_retention_period = var.backup_retention_period
  deletion_protection     = var.deletion_protection
  skip_final_snapshot     = var.skip_final_snapshot

  auto_minor_version_upgrade = true
  apply_immediately          = var.apply_immediately

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-postgres"
  })
}

# After RDS is available, Terraform reads the AWS-managed secret and uses psql to
# apply the canonical repo schema. The file hash makes schema edits rerun cleanly.
resource "terraform_data" "schema" {
  count = var.initialize_schema ? 1 : 0

  triggers_replace = [
    aws_db_instance.this.id,
    filesha256(local.schema_file_path)
  ]

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-NoProfile", "-Command"]
    command     = <<-EOT
      $secretJson = aws secretsmanager get-secret-value --secret-id '${aws_db_instance.this.master_user_secret[0].secret_arn}' --query SecretString --output text
      $secret = $secretJson | ConvertFrom-Json
      $env:PGPASSWORD = $secret.password
      $psql = '${var.psql_command}'
      & $psql -h '${aws_db_instance.this.address}' -p '${aws_db_instance.this.port}' -U '${var.master_username}' -d '${var.database_name}' -v ON_ERROR_STOP=1 -f '${local.schema_file_path}'
    EOT
  }
}

# Optional dev/test data load. Keep disabled for production-like environments.
resource "terraform_data" "seed" {
  count = var.initialize_seed_data ? 1 : 0

  triggers_replace = [
    aws_db_instance.this.id,
    filesha256(local.seed_file_path)
  ]

  depends_on = [terraform_data.schema]

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-NoProfile", "-Command"]
    command     = <<-EOT
      $secretJson = aws secretsmanager get-secret-value --secret-id '${aws_db_instance.this.master_user_secret[0].secret_arn}' --query SecretString --output text
      $secret = $secretJson | ConvertFrom-Json
      $env:PGPASSWORD = $secret.password
      $psql = '${var.psql_command}'
      & $psql -h '${aws_db_instance.this.address}' -p '${aws_db_instance.this.port}' -U '${var.master_username}' -d '${var.database_name}' -v ON_ERROR_STOP=1 -f '${local.seed_file_path}'
    EOT
  }
}
