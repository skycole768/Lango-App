# AWS region
variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

# Lambda settings
variable "lambda_runtime" {
  description = "The runtime environment for Lambda functions"
  type        = string
  default     = "python3.9"
}

variable "lambda_source_folder" {
  description = "Path to the folder containing zipped Lambda function files"
  type        = string
  default     = "../backend/lambdas/zip"
}

# API Gateway settings
variable "api_name" {
  description = "The name of the API Gateway"
  type        = string
  default     = "LangoAPI"
}

variable "stage_name" {
  description = "The name of the deployment stage"
  type        = string
  default     = "dev"
}

# DynamoDB table
variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for flashcard data"
  type        = string
  default     = "LangoAppTable"
}

variable "jwt_secret" {
  description = "Secret key to sign JWT tokens"
  type        = string
  sensitive   = true
}

variable "lambda_names" {
  default = [
    "add_flashcard",
    "edit_flashcard",
    "delete_flashcard",
    "get_flashcards",
    "get_flashcard",
    "add_set",
    "edit_set",
    "delete_set",
    "get_sets",
    "get_set",
    "add_language",
    "delete_language",
    "get_languages",
    "delete_user",
    "edit_user",
    "get_user",
    "signup",
    "login"
  ]
}