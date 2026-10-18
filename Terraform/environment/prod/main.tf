

module "network" {
  source = "../../modules/network"

  vpc_name              = var.vpc_name
  vpc_cidr              = var.vpc_cidr
  public_subnet_cidr    = var.public_subnet_cidr
  private_subnet_a_cidr = var.private_subnet_a_cidr
  private_subnet_b_cidr = var.private_subnet_b_cidr
}




module "security" {
  source = "../../modules/security"

  vpc_id            = module.network.vpc_id
  web_ingress_rules = var.web_ingress_rules
  app_ingress_rules = var.app_ingress_rules
  rds_ingress_rules = var.rds_ingress_rules
}



module "compute" {
  source = "../../modules/compute"

  web_ami_id        = var.web_ami_id
  app_ami_id        = var.app_ami_id
  instance_type     = var.instance_type
  key_name          = var.key_name
  web_private_ip    = var.web_private_ip
  app_private_ip    = var.app_private_ip
  web_instance_name = var.web_instance_name
  app_instance_name = var.app_instance_name

  public_subnet_id    = module.network.public_subnet_id
  private_subnet_a_id = module.network.private_subnet_a_id

  web_security_group_id = module.security.web_security_group_id
  app_security_group_id = module.security.app_security_group_id
}


module "database" {
  source = "../../modules/database"

  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage

  db_security_group_id = module.security.rds_security_group_id
  db_subnet_group_name = aws_db_subnet_group.starcourt_db_subnet_group.name
}


#--------rds sunet group------

resource "aws_db_subnet_group" "starcourt_db_subnet_group" {
  name        = "starcourt-tf-lab-db-subnet-group"
  description = "Private subnets for Starcourt PostgreSQL RDS"

  subnet_ids = [
    module.network.private_subnet_a_id,
    module.network.private_subnet_b_id
  ]

  tags = {
    Name = "starcourt-db-subnet-group"
  }
}

