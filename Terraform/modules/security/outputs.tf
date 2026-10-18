output "web_security_group_id" {
  value = aws_security_group.starcourt_web_sg.id
}

output "app_security_group_id" {
  value = aws_security_group.starcourt_app_sg.id
}

output "rds_security_group_id" {
  value = aws_security_group.starcourt_rds_sg.id
}