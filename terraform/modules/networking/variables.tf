variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
}

variable "availability_zone" {
  description = "Availability zone for the public subnet."
  type        = string
}

variable "secondary_public_subnet_cidr" {
  description = "CIDR block for the secondary public subnet used by services that require multiple AZs."
  type        = string
  default     = null
}

variable "secondary_availability_zone" {
  description = "Availability zone for the secondary public subnet."
  type        = string
  default     = null
}

variable "admin_cidr" {
  description = "Trusted CIDR block allowed to SSH to EC2 instances."
  type        = string
}

variable "common_tags" {
  description = "Common tags applied to all supported resources."
  type        = map(string)
  default     = {}
}
