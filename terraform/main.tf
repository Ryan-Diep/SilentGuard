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
# VPC setup
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnet_cidr_block
  availability_zone = var.availability_zone
  tags = {
    Name = "private-subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "vpc-igw"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = var.allowed_ip_range
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "private_subnet_association" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}


#############################################################################################
# IAM roles and policies setup
# IAM Role for Lambda VPC Access
resource "aws_security_group" "lambda_sg" {
  name_prefix = "lambda-sg"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr_block] # Should allow all within VPC
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.allowed_ip_range]
  }
}


#############################################################################################
# Lambda functions setup
# Lambda IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

# Attach Policies to Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda for Message Handling
resource "aws_lambda_function" "message_handler" {
  filename      = "file.zip" # need to upload a zipped Lambda function?? TODO !!
  function_name = "message_handler"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"


  environment {
    variables = {
      VPC_ID = aws_vpc.main.id
      REGION = var.region
    }
  }

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
}

# Lambda for Authorization
resource "aws_lambda_function" "authorizer_lambda" {
  filename      = "file.zip" # TODO !!
  function_name = "authorizer_lambda"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_role.arn
  handler       = "auth.lambda_handler"

  environment {
    variables = {
      AUTH_TOKEN = "some sort of solace secret?" # TODO!!
    }
  }
}


#############################################################################################
# API Gateway setup
# Create API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "SolaceHttpAPI"
  protocol_type = "HTTP"
}

# Integrate Main Lambda with API Gateway
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.message_handler.invoke_arn
}

# Lambda Authorizer
resource "aws_apigatewayv2_authorizer" "lambda_authorizer" {
  api_id           = aws_apigatewayv2_api.http_api.id
  authorizer_type  = "REQUEST"
  name             = "SolaceAuthorizer"
  authorizer_uri   = aws_lambda_function.authorizer_lambda.invoke_arn
  identity_sources = ["$request.header.Authorization"]
}

# Attach Authorizer and Integration to a Route
resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /process-message"

  target = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Stage Deployment -> might not be needed?
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "terraform-stage"
  auto_deploy = true
}


#############################################################################################
# Get link for API Gateway to connect to solace
output "api_gateway_url" {
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
  description = "URL for the deployed API Gateway"
}
