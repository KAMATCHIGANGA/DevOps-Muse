variable "vpc_id" {
  type = string
}

variable "web_ingress_rules" {
  type = list(object({
    description = string
    port        = number
    cidr        = string
  }))
}

variable "app_ingress_rules" {
  type = list(object({
    description = string
    port        = number
  }))
}

variable "rds_ingress_rules" {
  type = list(object({
    description = string
    port        = number
  }))
}