variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where PostgreSQL will run."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the RDS subnet group. RDS requires at least two AZs."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least two subnet IDs are required for the RDS subnet group."
  }
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to PostgreSQL."
  type        = list(string)
}

variable "database_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "quantshield"
}

variable "master_username" {
  description = "PostgreSQL master username. The password is managed by AWS Secrets Manager."
  type        = string
  default     = "quantshield_admin"
}

variable "engine_version" {
  description = "RDS PostgreSQL engine version. Null lets AWS choose the current default."
  type        = string
  default     = null
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial allocated storage in GiB."
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum autoscaled storage in GiB."
  type        = number
  default     = 100
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups."
  type        = number
  default     = 7
}

variable "publicly_accessible" {
  description = "Whether the dev database receives a public endpoint."
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "Whether deletion protection is enabled for the database."
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Whether to skip the final snapshot on destroy."
  type        = bool
  default     = true
}

variable "apply_immediately" {
  description = "Whether RDS modifications should apply immediately."
  type        = bool
  default     = true
}

variable "initialize_schema" {
  description = "Whether Terraform should run schema.sql after creating the database."
  type        = bool
  default     = true
}

variable "initialize_seed_data" {
  description = "Whether Terraform should run seed_data.sql after the schema is initialized. Intended for dev/testing only."
  type        = bool
  default     = false
}

variable "schema_file_path" {
  description = "Optional absolute path to the SQL schema file. Defaults to the repo-level sql/schema.sql from the dev environment."
  type        = string
  default     = null
}

variable "seed_file_path" {
  description = "Optional absolute path to the SQL seed file. Defaults to the repo-level sql/seed_data.sql from the dev environment."
  type        = string
  default     = null
}

variable "psql_command" {
  description = "psql executable used by local-exec schema and seed initialization. Use an absolute path on Windows when psql is not on PATH."
  type        = string
  default     = "psql"
}

variable "common_tags" {
  description = "Common tags applied to all supported resources."
  type        = map(string)
  default     = {}
}
