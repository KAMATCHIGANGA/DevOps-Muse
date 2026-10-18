output "vpc_id" {
  description = "ID of the Starcourt VPC"
  value       = module.network.vpc_id
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = module.network.public_subnet_id
}

output "private_subnet_a_id" {
  description = "ID of private subnet A"
  value       = module.network.private_subnet_a_id
}

output "private_subnet_b_id" {
  description = "ID of private subnet B"
  value       = module.network.private_subnet_b_id
}

output "web_instance_id" {
  value = module.compute.web_instance_id
}

output "web_public_ip" {
  value = module.compute.web_public_ip
}

output "app_instance_id" {
  value = module.compute.app_instance_id
}

output "app_private_ip" {
  value = module.compute.app_private_ip
}

output "rds_endpoint" {
  description = "Endpoint of the Starcourt PostgreSQL database"
  value       = module.database.rds_endpoint
}