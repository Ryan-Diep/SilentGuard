variable "region" {
  description = "AWS region to deploy to"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block for VPC"
  type        = string
}

variable "subnet_cidr_block" {
  description = "CIDR block for the subnet"
  type        = string
}

variable "availability_zone" {
  description = "Availability zone for the subnet"
  type        = string
}

variable "solace_username" {
  description = "Solace username"
  type        = string
  default     = "solace-cloud-client"
}

variable "solace_password" {
  description = "Solace password"
  type        = string
}

variable "solace_url" {
  description = "Solace url"
  type        = string
}

variable "solace_port" {
  description = "Solace port"
  type        = string
}

variable "groq_api_key" {
  description = "Groq API key"
  type        = string
}