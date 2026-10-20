#-----------rds--------------------
resource "aws_db_instance" "starcourt_db" {
  identifier = "starcourt-tf-lab-db"

  engine         = "postgres"
  instance_class = var.db_instance_class

  allocated_storage = var.db_allocated_storage
  db_name           = var.db_name
  username          = var.db_username
  password          = var.db_password
  port              = 5432

  vpc_security_group_ids = [var.db_security_group_id]
  db_subnet_group_name   = var.db_subnet_group_name
  publicly_accessible    = false

  skip_final_snapshot = true

  tags = {
    Name = "starcourt-tf-lab-db"
  }
}
