module "vpc" {
  source               = "terraform-aws-modules/vpc/aws"
  version              = "1.14.0"
  name                 = "eks-vpc"
  cidr                 = "192.168.0.0/16"
  
  azs                  = [
    "eu-west-1a",
    "eu-west-1b",
    "eu-west-1c",
  ]
  
  private_subnets      = [
    "192.168.64.0/18",
    "192.168.128.0/18",
    "192.168.192.0/18",
  ]
  
  public_subnets       = [
    "192.168.0.0/24"
  ]
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  enable_nat_gateway   = true
  single_nat_gateway   = true
}
