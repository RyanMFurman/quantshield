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
