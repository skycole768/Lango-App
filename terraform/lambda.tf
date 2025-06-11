locals {
  lambda_functions = {

    add_flashcard = {
      zip     = "flashcard.zip"
      handler = "handler.add_flashcard"
    }
    edit_flashcard = {
      zip     = "flashcard.zip"
      handler = "handler.edit_flashcard"
    }
    delete_flashcard = {
      zip     = "flashcard.zip"
      handler = "handler.delete_flashcard"
    }
    get_flashcards = {
      zip     = "flashcard.zip"
      handler = "handler.get_flashcards"
    }
    get_flashcard = {
      zip     = "flashcard.zip"
      handler = "handler.get_flashcard"
    }

    add_set = {
      zip     = "set.zip"
      handler = "handler.add_set"
    }
    edit_set = {
      zip     = "set.zip"
      handler = "handler.edit_set"
    }
    delete_set = {
      zip     = "set.zip"
      handler = "handler.delete_set"
    }
    get_sets = {
      zip     = "set.zip"
      handler = "handler.get_sets"
    }
    get_set = {
      zip     = "set.zip"
      handler = "handler.get_set"
    }

    add_language = {
      zip     = "language.zip"
      handler = "handler.add_language"
    }
    delete_language = {
      zip     = "language.zip"
      handler = "handler.delete_language"
    }
    get_languages = {
      zip     = "language.zip"
      handler = "handler.get_languages"
    }
    get_language = {
      zip     = "language.zip"
      handler = "handler.get_language"
    }

    add_user = {
      zip     = "user.zip"
      handler = "handler.add_user"
    }
    delete_user = {
      zip     = "user.zip"
      handler = "handler.delete_user"
    }

    edit_user = {
      zip     = "user.zip"
      handler = "handler.edit_user"
    }
    get_user = {
      zip     = "user.zip"
      handler = "handler.get_user"
    }

    signup = {
      zip     = "auth.zip"
      handler = "handler.signup"
    }
    login = {
      zip     = "auth.zip"
      handler = "handler.login"
    }
  }
}

resource "aws_lambda_function" "lango_functions" {
   for_each      = local.lambda_functions

  function_name = "${each.key}Function"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = each.value.handler
  runtime       = var.lambda_runtime
  filename      = "${var.lambda_source_folder}/${each.value.zip}"

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.lango_table.name
    }
  }

  source_code_hash = filebase64sha256("${var.lambda_source_folder}/${each.value.zip}")

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_iam_role_policy_attachment.lambda_policy_attachment
  ]
}

resource "aws_lambda_function" "auth_lambda" {
  function_name = "LangoAuthLambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "auth.handler"
  runtime       = var.lambda_runtime
  filename      = "${var.lambda_source_folder}/auth.zip"

  source_code_hash = filebase64sha256("${var.lambda_source_folder}/auth.zip")
}

resource "aws_lambda_permission" "auth_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lango_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_authorizer" "lango_authorizer" {
  api_id        = aws_apigatewayv2_api.lango_api.id
  name          = "LangoLambdaAuthorizer"
  authorizer_type = "REQUEST"
  authorizer_uri  = aws_lambda_function.auth_lambda.invoke_arn
  identity_sources = ["$request.header.Authorization"]

  authorizer_payload_format_version = "2.0"
  enable_simple_responses = true
}




