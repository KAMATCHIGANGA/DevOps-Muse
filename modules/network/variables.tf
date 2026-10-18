variable "vpc_name" {
  description = "Name of the Starcourt VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR range of the Starcourt VPC"
  type        = string
}

variable "public_subnet_cidr" {
  type = string
}

variable "private_subnet_a_cidr" {
  type = string
}

variable "private_subnet_b_cidr" {
  type = string
}