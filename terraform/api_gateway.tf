resource "aws_apigatewayv2_api" "lango_api" {
  name          = var.api_name
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["*"]
  }
  
}

locals {
  lango_endpoints = {
    addFlashcard     = { method = "POST",    lambda = aws_lambda_function.lango_functions["add_flashcard"] }
    editFlashcard    = { method = "PUT",     lambda = aws_lambda_function.lango_functions["edit_flashcard"]}
    deleteFlashcard  = { method = "DELETE",  lambda = aws_lambda_function.lango_functions["delete_flashcard"]}
    getFlashcards    = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_flashcards"]}
    getFlashcard     = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_flashcard"]}

    addSet           = { method = "POST",    lambda = aws_lambda_function.lango_functions["add_set"]}
    getSets          = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_sets"]}
    getSet           = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_set"]}
    editSet          = { method = "PUT",     lambda = aws_lambda_function.lango_functions["edit_set"]}
    deleteSet        = { method = "DELETE",  lambda = aws_lambda_function.lango_functions["delete_set"]}

    addLanguage      = { method = "POST",    lambda = aws_lambda_function.lango_functions["add_language"]}
    getLanguages     = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_languages"]}
    deleteLanguage   = { method = "DELETE",  lambda = aws_lambda_function.lango_functions["delete_language"]}

    deleteUser       = { method = "DELETE",  lambda = aws_lambda_function.lango_functions["delete_user"]}
    editUser      = { method = "PUT",     lambda = aws_lambda_function.lango_functions["edit_user"]}
    getUser       = { method = "GET",     lambda = aws_lambda_function.lango_functions["get_user"]}

    signup = { method = "POST", lambda = aws_lambda_function.lango_functions["signup"]}
    login  = { method = "POST", lambda = aws_lambda_function.lango_functions["login"]}
  }
}

resource "aws_lambda_permission" "lango_permissions" {
  for_each = local.lango_endpoints

  statement_id  = "Allow${each.key}Invoke"
  action        = "lambda:InvokeFunction"
  function_name = each.value.lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lango_api.execution_arn}/*/*"
}


resource "aws_apigatewayv2_integration" "lango_integrations" {
  for_each = local.lango_endpoints

  api_id                  = aws_apigatewayv2_api.lango_api.id
  integration_type        = "AWS_PROXY"
  integration_uri         = each.value.lambda.invoke_arn
  payload_format_version  = "2.0"
}


resource "aws_apigatewayv2_route" "lango_routes" {
  for_each = local.lango_endpoints

  api_id    = aws_apigatewayv2_api.lango_api.id
  route_key = "${each.value.method} /${each.key}"
  target    = "integrations/${aws_apigatewayv2_integration.lango_integrations[each.key].id}"
}

resource "aws_apigatewayv2_stage" "lango_stage" {
  api_id = aws_apigatewayv2_api.lango_api.id
  name   = var.stage_name

  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 5000
    throttling_rate_limit  = 10000
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format           = jsonencode({
      requestId = "$context.requestId",
      ip       = "$context.identity.sourceIp",
      method   = "$context.httpMethod",
      resource = "$context.resourcePath",
      status   = "$context.status"
    })
  }
}