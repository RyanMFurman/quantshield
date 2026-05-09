output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_id" {
  description = "ID of the public subnet."
  value       = aws_subnet.public["primary"].id
}

output "public_subnet_ids" {
  description = "IDs of all public subnets."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "internet_gateway_id" {
  description = "ID of the internet gateway."
  value       = aws_internet_gateway.this.id
}

output "public_route_table_id" {
  description = "ID of the public route table."
  value       = aws_route_table.public.id
}

output "ec2_public_security_group_id" {
  description = "ID of the EC2 public security group."
  value       = aws_security_group.ec2_public.id
}
