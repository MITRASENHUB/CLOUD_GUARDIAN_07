# EC2 Instances Configuration

# EC2 IAM Instance Profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2_instance.name
  
  tags = local.common_tags
}

# Web Tier EC2 Instances
resource "aws_instance" "web" {
  count                  = var.ec2_instance_count
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.ec2_instance_type
  subnet_id              = aws_subnet.public[count.index % length(aws_subnet.public)].id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  
  # MISCONFIGURATION 5: Unencrypted EBS volumes
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 8
    encrypted             = var.misconfig_disable_encryption ? false : true
    delete_on_termination = true
  }
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>CloudGuardian Web Server ${count.index + 1}</h1>" > /var/www/html/index.html
              EOF
  
  tags = merge(
    local.common_tags,
    {
      Name                = "${local.name_prefix}-web-${count.index + 1}"
      Misconfiguration    = "Unencrypted EBS Volume"
      MisconfigurationID  = "EC2-001"
    }
  )
}

# Elastic IPs for EC2 instances
resource "aws_eip" "web" {
  count    = var.ec2_instance_count
  instance = aws_instance.web[count.index].id
  domain   = "vpc"
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-web-eip-${count.index + 1}"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}
