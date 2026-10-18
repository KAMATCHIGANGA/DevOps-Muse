output "web_instance_id" {
  value = aws_instance.starcourt_web_ec2.id
}

output "web_public_ip" {
  value = aws_instance.starcourt_web_ec2.public_ip
}

output "app_instance_id" {
  value = aws_instance.starcourt_app_ec2.id
}

output "app_private_ip" {
  value = aws_instance.starcourt_app_ec2.private_ip
}