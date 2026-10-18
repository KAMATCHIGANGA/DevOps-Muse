#----WEB SG---------

resource "aws_security_group" "starcourt_web_sg" {
  name        = "starcourt-tf-lab-web-sg"
  description = "HTTP and restricted SSH access for Starcourt"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.web_ingress_rules

    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = [ingress.value.cidr]
    }
  }

  egress {
    description = "Allow outbound IPv4 traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "starcourt-tf-lab-web-sg"
  }
}

#---------app sg-----------

resource "aws_security_group" "starcourt_app_sg" {
  name        = "starcourt-tf-lab-app-sg"
  description = "Allow SSH and application traffic from Web EC2"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.app_ingress_rules

    content {
      description     = ingress.value.description
      from_port       = ingress.value.port
      to_port         = ingress.value.port
      protocol        = "tcp"
      security_groups = [aws_security_group.starcourt_web_sg.id]
    }
  }

  egress {
    description = "Allow outbound IPv4 traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "starcourt-tf-lab-app-sg"
  }
}

#--rds sg----

resource "aws_security_group" "starcourt_rds_sg" {
  name        = "starcourt-tf-lab-rds-sg"
  description = "Allow PostgreSQL access from the Starcourt App EC2"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.rds_ingress_rules

    content {
      description     = ingress.value.description
      from_port       = ingress.value.port
      to_port         = ingress.value.port
      protocol        = "tcp"
      security_groups = [aws_security_group.starcourt_app_sg.id]
    }
  }

  egress {
    description = "Allow outbound IPv4 traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "starcourt-tf-lab-rds-sg"
  }
}