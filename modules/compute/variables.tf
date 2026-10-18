variable "web_ami_id" {
  type = string
}

variable "app_ami_id" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "key_name" {
  type = string
}

variable "web_private_ip" {
  type = string
}

variable "app_private_ip" {
  type = string
}

variable "web_instance_name" {
  type = string
}

variable "app_instance_name" {
  type = string
}

variable "public_subnet_id" {
  type = string
}

variable "private_subnet_a_id" {
  type = string
}

variable "web_security_group_id" {
  type = string
}

variable "app_security_group_id" {
  type = string
}