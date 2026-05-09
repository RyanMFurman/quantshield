variable "project_name" {
  # Used with environment to create predictable IAM resource names.
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  # Separates dev/stage/prod IAM names and policy resource ARNs.
  description = "Deployment environment name."
  type        = string
}

variable "lambda_function_names" {
  # Required so Lambda log permissions cannot expand to every function by accident.
  description = "Lambda function names this module should allow to write CloudWatch logs."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.lambda_function_names) > 0
    error_message = "At least one Lambda function name is required so the Lambda log policy is not unconstrained."
  }
}

variable "github_repository" {
  # GitHub OIDC subjects use owner/repo, so reject organization-wide trust.
  description = "GitHub repository allowed to assume the deploy role, formatted as owner/repo."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "github_repository must be formatted as owner/repo."
  }
}

variable "github_allowed_refs" {
  # Default to main; add release branches or tags only when workflows need them.
  description = "Git refs allowed to assume the deploy role, such as refs/heads/main."
  type        = list(string)
  default     = ["refs/heads/main"]

  validation {
    condition     = length(var.github_allowed_refs) > 0 && alltrue([for ref in var.github_allowed_refs : startswith(ref, "refs/heads/") || startswith(ref, "refs/tags/")])
    error_message = "github_allowed_refs must contain one or more refs/heads/* or refs/tags/* values."
  }
}

variable "github_oidc_provider_arn" {
  # Use this when an AWS account already has a shared GitHub Actions OIDC provider.
  description = "Existing GitHub Actions OIDC provider ARN. Leave null to create token.actions.githubusercontent.com in this module."
  type        = string
  default     = null
}

variable "github_oidc_thumbprints" {
  # AWS provider v5 can discover GitHub thumbprints when this is null.
  description = "Optional thumbprints for the GitHub Actions OIDC provider when this module creates it. Leave null for providers that do not require explicit thumbprints."
  type        = list(string)
  default     = null
}

variable "common_tags" {
  # Tags help identify ownership and environment for IAM resources that support tagging.
  description = "Common tags applied to all supported resources."
  type        = map(string)
  default     = {}
}
