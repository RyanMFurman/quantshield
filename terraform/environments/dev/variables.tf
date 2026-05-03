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

variable "admin_cidr" {
  description = "Trusted CIDR block allowed to SSH to EC2 instances. Replace the example value before planning real infrastructure."
  type        = string
  default     = "203.0.113.10/32"
}

variable "common_tags" {
  description = "Additional tags to apply to supported resources."
  type        = map(string)
  default = {
    Owner = "Ryan"
  }
}
