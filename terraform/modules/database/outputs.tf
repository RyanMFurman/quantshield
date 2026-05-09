output "db_instance_id" {
  description = "ID of the PostgreSQL RDS instance."
  value       = aws_db_instance.this.id
}

output "db_endpoint" {
  description = "PostgreSQL endpoint hostname."
  value       = aws_db_instance.this.address
}

output "db_port" {
  description = "PostgreSQL endpoint port."
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "PostgreSQL database name."
  value       = aws_db_instance.this.db_name
}

output "db_secret_arn" {
  description = "Secrets Manager ARN for the RDS-managed master user credentials."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
  sensitive   = true
}

output "db_security_group_id" {
  description = "Security group ID for PostgreSQL."
  value       = aws_security_group.postgres.id
}
