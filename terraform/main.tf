terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "eu-north-1"
}

# ==================================================
# S3
# ==================================================

resource "aws_s3_bucket" "cloudops" {
  bucket = "cloudops-nadhanizaar-2026"

  tags = {
    Name        = "CloudOps Enterprise Platform"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# ==================================================
# LAMBDA
# ==================================================

resource "aws_lambda_function" "cloudops_lambda" {
  function_name = "cloudops-lambda"
  filename      = "cloudops-lambda.zip"

  role    = "arn:aws:iam::613025568873:role/service-role/cloudops-lambda-role-067f46dk"
  handler = "lambda_function.lambda_handler"
  runtime = "python3.13"

  timeout     = 3
  memory_size = 128

  architectures = ["x86_64"]

  lifecycle {
    ignore_changes = all
  }
}

# ==================================================
# API GATEWAY
# ==================================================

resource "aws_apigatewayv2_api" "cloudops_api" {
  name          = "cloudops-api"
  protocol_type = "HTTP"

  lifecycle {
    ignore_changes = all
  }
}

# ==================================================
# API → LAMBDA INTEGRATION
# ==================================================

resource "aws_apigatewayv2_integration" "cloudops_lambda_integration" {
  api_id = aws_apigatewayv2_api.cloudops_api.id

  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.cloudops_lambda.arn

  payload_format_version = "2.0"

  lifecycle {
    ignore_changes = all
  }
}

# ==================================================
# GET /hello ROUTE
# ==================================================

resource "aws_apigatewayv2_route" "cloudops_hello" {
  api_id    = aws_apigatewayv2_api.cloudops_api.id
  route_key = "GET /hello"

  target = "integrations/${aws_apigatewayv2_integration.cloudops_lambda_integration.id}"

  lifecycle {
    ignore_changes = all
  }
}

# ==================================================
# DEFAULT API STAGE
# ==================================================

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.cloudops_api.id
  name        = "$default"
  auto_deploy = true

  lifecycle {
    ignore_changes = all
  }
}

# ==================================================
# CLOUDOPS API STAGE
# ==================================================

resource "aws_apigatewayv2_stage" "cloudops" {
  api_id      = aws_apigatewayv2_api.cloudops_api.id
  name        = "stage-cloudOps"
  auto_deploy = true

  lifecycle {
    ignore_changes = all
  }
}
