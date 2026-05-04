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
