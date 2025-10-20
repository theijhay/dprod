# CodeDeploy Application
resource "aws_codedeploy_app" "dprod_app" {
  compute_platform = "Server"
  name             = "dprod-app"

  tags = {
    Name = "dprod-app"
  }
}

# CodeDeploy Deployment Group
resource "aws_codedeploy_deployment_group" "dprod_deployment_group" {
  app_name              = aws_codedeploy_app.dprod_app.name
  deployment_group_name = "dprod-deployment-group"
  service_role_arn      = aws_iam_role.codedeploy_service_role.arn

  ec2_tag_filter {
    key   = "Name"
    type  = "KEY_AND_VALUE"
    value = "dprod-server"
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "IN_PLACE"
  }

  tags = {
    Name = "dprod-deployment-group"
  }
}

# Output CodeDeploy application name
output "codedeploy_app_name" {
  value = aws_codedeploy_app.dprod_app.name
}

output "codedeploy_deployment_group_name" {
  value = aws_codedeploy_deployment_group.dprod_deployment_group.deployment_group_name
}
