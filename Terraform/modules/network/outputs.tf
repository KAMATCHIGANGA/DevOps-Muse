output "vpc_id" {
  value = aws_vpc.starcourt_vpc.id
}

output "public_subnet_id" {
  value = aws_subnet.starcourt_public_a.id
}

output "private_subnet_a_id" {
  value = aws_subnet.starcourt_private_a.id
}

output "private_subnet_b_id" {
  value = aws_subnet.starcourt_private_b.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.starcourt_igw.id
}

output "public_route_table_id" {
  value = aws_route_table.starcourt_public_rtb.id
}

output "private_route_table_id" {
  value = aws_route_table.starcourt_private_rtb.id
}

output "nat_gateway_id" {
  value = aws_nat_gateway.starcourt_nat.id
}

output "nat_eip" {
  value = aws_eip.starcourt_nat_eip.public_ip
}