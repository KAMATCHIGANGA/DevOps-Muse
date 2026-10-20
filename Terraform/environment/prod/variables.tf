variable "aws_region" {
  description = "AWS region for the existing Starcourt infrastructure"
  type        = string
  default     = "ap-southeast-2"
}

variable "vpc_name" {
  description = "Name of the existing Starcourt VPC"
  type        = string
  default     = "starcourt-tf-lab-vpc"
}

variable "vpc_cidr" {
  description = "CIDR range of the existing VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR of the public subnet"
  type        = string
  default     = "10.20.1.0/24"
}

variable "private_subnet_a_cidr" {
  description = "CIDR of private subnet A"
  type        = string
  default     = "10.20.10.0/24"
}

variable "private_subnet_b_cidr" {
  description = "CIDR of private subnet B"
  type        = string
  default     = "10.20.11.0/24"
}

variable "instance_type" {
  description = "EC2 instance type used by Starcourt"
  type        = string
  default     = "t3.micro"
}

variable "web_ingress_rules" {
  description = "Ingress rules for the Starcourt web security group"

  type = list(object({
    description = string
    port        = number
    cidr        = string
  }))

  default = [
    {
      description = "HTTP from the internet"
      port        = 80
      cidr        = "0.0.0.0/0"
    }
  ]
}


variable "app_ingress_rules" {
  description = "Ingress rules for the Starcourt application security group"

  type = list(object({
    description = string
    port        = number
  }))

  default = [
    {
      description = "SSH from Web security group"
      port        = 22
    },
    {
      description = "Flask traffic from Web security group"
      port        = 5000
    }
  ]
}

variable "rds_ingress_rules" {
  description = "Ingress rules for the Starcourt PostgreSQL security group"

  type = list(object({
    description = string
    port        = number
  }))

  default = [
    {
      description = "PostgreSQL from App security group"
      port        = 5432
    }
  ]
}

variable "web_instance_name" {
  description = "Name of the Starcourt public web EC2 instance"
  type        = string
  default     = "starcourt-tf-lab-web"
}

variable "app_instance_name" {
  description = "Name of the Starcourt private application EC2 instance"
  type        = string
  default     = "starcourt-tf-lab-app"
}

variable "web_ami_id" {
  description = "AMI ID for the Starcourt web EC2 instance"
  type        = string
}

variable "app_ami_id" {
  description = "AMI ID for the Starcourt application EC2 instance"
  type        = string
}

variable "key_name" {
  description = "Name of the existing EC2 key pair"
  type        = string
}

variable "web_private_ip" {
  description = "Private IPv4 address of the web EC2 instance"
  type        = string
  default     = "10.20.1.42"
}

variable "app_private_ip" {
  description = "Private IPv4 address of the application EC2 instance"
  type        = string
  default     = "10.20.10.252"
}

variable "db_name" {
  description = "Initial PostgreSQL database name"
  type        = string
  default     = "postgres"
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "starcourtadmin"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated RDS storage in GiB"
  type        = number
  default     = 20
}