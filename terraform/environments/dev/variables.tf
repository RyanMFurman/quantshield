variable "project_name" {
  description = "Project name used for resource naming and tagging."
  type        = string
  default     = "quantshield"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the dev VPC."
  type        = string
  default     = "10.10.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the dev public subnet."
  type        = string
  default     = "10.10.1.0/24"
}

variable "availability_zone" {
  description = "Availability zone for the dev public subnet."
  type        = string
  default     = "us-east-1a"
}

variable "secondary_public_subnet_cidr" {
  description = "CIDR block for the secondary dev public subnet."
  type        = string
  default     = "10.10.2.0/24"
}

variable "secondary_availability_zone" {
  description = "Availability zone for the secondary dev public subnet."
  type        = string
  default     = "us-east-1b"
}

variable "admin_cidr" {
  description = "Trusted CIDR block allowed to SSH to EC2 instances. Replace the example value before planning real infrastructure."
  type        = string
  default     = "203.0.113.10/32"
}

variable "ec2_instance_type" {
  description = "Instance type for the temporary dev web reachability test instance."
  type        = string
  default     = "t3.micro"
}

variable "database_name" {
  description = "Initial PostgreSQL database name for dev."
  type        = string
  default     = "quantshield"
}

variable "rds_instance_class" {
  description = "RDS PostgreSQL instance class for dev."
  type        = string
  default     = "db.t4g.micro"
}

variable "initialize_seed_data" {
  description = "Whether to load sql/seed_data.sql into the dev database after schema initialization."
  type        = bool
  default     = false
}

variable "psql_command" {
  description = "psql executable used by Terraform when initializing the RDS schema and optional seed data."
  type        = string
  default     = "psql"
}

variable "lambda_function_names" {
  # Drives the Lambda log policy scope in the IAM module.
  description = "Lambda function names allowed to use the dev Lambda execution role."
  type        = list(string)
  default     = ["quantshield-dev-api"]
}

variable "github_repository" {
  # Restricts GitHub Actions OIDC trust to this repository.
  description = "GitHub repository allowed to assume the dev deploy role, formatted as owner/repo."
  type        = string
  default     = "RyanMFurman/quantshield"
}

variable "github_allowed_refs" {
  # Restricts deploy role assumption to known safe branches or tags.
  description = "Git refs allowed to assume the dev deploy role."
  type        = list(string)
  default     = ["refs/heads/main"]
}

variable "common_tags" {
  description = "Additional tags to apply to supported resources."
  type        = map(string)
  default = {
    Owner = "Ryan"
  }
}
