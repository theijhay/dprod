terraform {
  backend "s3" {
    bucket = "dprod-terraform-state-1760804533"
    key    = "dprod/terraform.tfstate"
    region = "us-east-1"
  }
}
