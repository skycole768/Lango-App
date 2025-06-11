output "api_endpoint" {
  description = "Base URL of the deployed Lango API"
  value       = aws_apigatewayv2_stage.lango_stage.invoke_url
}

output "lambda_function_names" {
  description = "List of deployed Lambda function names"
  value       = [for f in aws_lambda_function.lango_functions : f.function_name]
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.lango_table.name
}

