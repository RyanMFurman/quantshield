output "lambda_role_arn" {
  # Consumers use the ARN when attaching this role to Lambda functions.
  description = "ARN of the Lambda execution role."
  value       = aws_iam_role.lambda.arn
}

output "lambda_role_name" {
  # Exposes the stable role name for policy attachments outside this module.
  description = "Name of the Lambda execution role."
  value       = aws_iam_role.lambda.name
}

output "ec2_role_arn" {
  # Useful for audits and downstream modules that need the EC2 role identity.
  description = "ARN of the EC2 instance role."
  value       = aws_iam_role.ec2.arn
}

output "ec2_role_name" {
  # Exposes the stable EC2 role name for any future attachments.
  description = "Name of the EC2 instance role."
  value       = aws_iam_role.ec2.name
}

output "ec2_instance_profile_name" {
  # EC2 instances reference the profile name, not the role name.
  description = "Name of the EC2 instance profile."
  value       = aws_iam_instance_profile.ec2.name
}

output "github_actions_deploy_role_arn" {
  # Add this ARN to GitHub Actions secrets or environment configuration for deployments.
  description = "ARN of the GitHub Actions deploy role."
  value       = aws_iam_role.github_actions_deploy.arn
}

output "github_actions_deploy_role_name" {
  # Exposes the role name for AWS console checks and future policy attachments.
  description = "Name of the GitHub Actions deploy role."
  value       = aws_iam_role.github_actions_deploy.name
}

output "github_oidc_provider_arn" {
  # Shows whether this module created or reused the GitHub OIDC provider.
  description = "ARN of the GitHub Actions OIDC provider used by the deploy role."
  value       = local.github_oidc_provider_arn
}
