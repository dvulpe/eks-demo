module "eks" {
  source        = "terraform-aws-modules/eks/aws"
  version       = "1.6.0"
  
  cluster_name  = "test-eks-cluster"
  
  subnets       = [
    "${module.vpc.private_subnets}"]
  
  tags          = {
    Environment = "test"
  }
  
  vpc_id        = "${module.vpc.vpc_id}"
  
  worker_groups = [
    {
      "instance_type"       = "m5.large",
      "autoscaling_enabled" = true,
      "spot_price"          = "0.05"
    },
  ]
}
