resource "aws_vpc" "starcourt_vpc" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = var.vpc_name
  }
}

#-----------------------------------------------------------------
#-----------------SUBNET------------------------------------------
#-----------------------------------------------------------------

resource "aws_subnet" "starcourt_public_a" {
  vpc_id                  = aws_vpc.starcourt_vpc.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "ap-southeast-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "starcourt-public-a"
  }
}

resource "aws_subnet" "starcourt_private_a" {
  vpc_id            = aws_vpc.starcourt_vpc.id
  cidr_block        = var.private_subnet_a_cidr
  availability_zone = "ap-southeast-2a"

  tags = {
    Name = "starcourt-private-a"
  }
}

resource "aws_subnet" "starcourt_private_b" {
  vpc_id            = aws_vpc.starcourt_vpc.id
  cidr_block        = var.private_subnet_b_cidr
  availability_zone = "ap-southeast-2b"

  tags = {
    Name = "starcourt-private-b"
  }
}

#------INTERNET-GATEWAY----------------------
resource "aws_internet_gateway" "starcourt_igw" {
  vpc_id = aws_vpc.starcourt_vpc.id

  tags = {
    Name = "starcourt-igw"
  }
}

#-------PUBLIC rtb--------------------------
resource "aws_route_table" "starcourt_public_rtb" {
  vpc_id = aws_vpc.starcourt_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.starcourt_igw.id
  }

  tags = {
    Name = "starcourt-public-rtb"
  }
}

#---------rtb subnet association--------

resource "aws_route_table_association" "starcourt_public_a_association" {
  subnet_id      = aws_subnet.starcourt_public_a.id
  route_table_id = aws_route_table.starcourt_public_rtb.id
}

#------------NAT GATEWAY AND ELASTIC IP ------------------

resource "aws_eip" "starcourt_nat_eip" {
  domain = "vpc"

  tags = {
    Name = "starcourt-nat-eip"
  }
}

resource "aws_nat_gateway" "starcourt_nat" {
  allocation_id = aws_eip.starcourt_nat_eip.id
  subnet_id     = aws_subnet.starcourt_public_a.id

  tags = {
    Name = "starcourt-nat"
  }
}

#----------PRIVATE RTB------------

resource "aws_route_table" "starcourt_private_rtb" {
  vpc_id = aws_vpc.starcourt_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.starcourt_nat.id
  }

  tags = {
    Name = "starcourt-private-rtb"
  }
}

#--------ASSOCIATION-----------

resource "aws_route_table_association" "starcourt_private_a_association" {
  subnet_id      = aws_subnet.starcourt_private_a.id
  route_table_id = aws_route_table.starcourt_private_rtb.id
}

resource "aws_route_table_association" "starcourt_private_b_association" {
  subnet_id      = aws_subnet.starcourt_private_b.id
  route_table_id = aws_route_table.starcourt_private_rtb.id
}