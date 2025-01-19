terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.region
}

#############################################################################################
# Lambda Layer for Groq
resource "aws_lambda_layer_version" "groq_layer" {
  filename            = "${path.module}/../lambdas/libraries.zip"
  compatible_runtimes = ["python3.13"]
  layer_name          = "groq-layer"
}

#############################################################################################
# Lambda Function for Message Handling
data "archive_file" "lambda_function" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/lambda_function.py"
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "message_handler" {
  filename      = "lambda_function.zip"
  function_name = "message_handler"
  runtime       = "python3.13"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"

  # Attach the Groq layer
  layers = [
    aws_lambda_layer_version.groq_layer.arn
  ]

  environment {
    variables = {
      API_KEY = var.groq_api_key
    }
  }
}

#############################################################################################
# IAM Role and Policy for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_execution_policy" {
  name = "lambda_execution_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}

#############################################################################################
# API Gateway Setup
resource "aws_apigatewayv2_api" "http_api" {
  name          = "SolaceHttpAPI"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.message_handler.invoke_arn
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /process-message"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "default"
  auto_deploy = true
}

#############################################################################################
# Outputs
output "api_gateway_url" {
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
  description = "URL for the deployed API Gateway"
}
