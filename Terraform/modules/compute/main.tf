#-------ec2------------

resource "aws_instance" "starcourt_web_ec2" {
  ami                         = var.web_ami_id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [var.web_security_group_id]
  private_ip                  = var.web_private_ip
  associate_public_ip_address = true

  tags = {
    Name = var.web_instance_name
  }
}

resource "aws_instance" "starcourt_app_ec2" {
  ami                    = var.app_ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = var.private_subnet_a_id
  vpc_security_group_ids = [var.app_security_group_id]
  private_ip             = var.app_private_ip

  associate_public_ip_address = false

  tags = {
    Name = var.app_instance_name
  }
}
