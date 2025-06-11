resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/lango-api-logs"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/lango-lambda-logs"
  retention_in_days = 14
}
