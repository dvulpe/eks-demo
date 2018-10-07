provider "aws" {
  region  = "eu-west-1"
  version = "~> 1.39"
}

terraform {
  backend "local" {
    path = ".terraform-state"
  }
}