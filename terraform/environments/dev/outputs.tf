output "vpc_id" {
  description = "ID of the dev VPC."
  value       = module.networking.vpc_id
}

output "public_subnet_id" {
  description = "ID of the dev public subnet."
  value       = module.networking.public_subnet_id
}

output "internet_gateway_id" {
  description = "ID of the dev internet gateway."
  value       = module.networking.internet_gateway_id
}

output "public_route_table_id" {
  description = "ID of the dev public route table."
  value       = module.networking.public_route_table_id
}

output "ec2_public_security_group_id" {
  description = "ID of the dev EC2 public security group."
  value       = module.networking.ec2_public_security_group_id
}

output "web_test_instance_id" {
  description = "ID of the temporary dev web reachability test instance."
  value       = aws_instance.web_test.id
}

output "web_test_public_ip" {
  description = "Public IP address for the temporary dev web reachability test instance."
  value       = aws_instance.web_test.public_ip
}

output "web_test_url" {
  description = "HTTP URL for the temporary dev web reachability test instance."
  value       = "http://${aws_instance.web_test.public_ip}"
}

output "lambda_role_arn" {
  # Exported so future Lambda functions can reuse the dev execution role.
  description = "ARN of the dev Lambda execution role."
  value       = module.iam.lambda_role_arn
}

output "ec2_role_arn" {
  # Confirms the EC2 workload role created for the dev environment.
  description = "ARN of the dev EC2 instance role."
  value       = module.iam.ec2_role_arn
}

output "ec2_instance_profile_name" {
  # Useful when checking the profile attached to the dev test instance.
  description = "Name of the dev EC2 instance profile."
  value       = module.iam.ec2_instance_profile_name
}

output "github_actions_deploy_role_arn" {
  # This ARN is what GitHub Actions should assume for Terraform deployments.
  description = "ARN of the dev GitHub Actions deploy role."
  value       = module.iam.github_actions_deploy_role_arn
}

output "github_oidc_provider_arn" {
  # Identifies the GitHub OIDC provider used by the deploy role trust policy.
  description = "ARN of the GitHub Actions OIDC provider used by the dev deploy role."
  value       = module.iam.github_oidc_provider_arn
}
