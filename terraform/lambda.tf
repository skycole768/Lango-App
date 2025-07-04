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
  timeout       = 10

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.lango_table.name
      JWT_SECRET          = var.jwt_secret
    }
  }

  source_code_hash = filebase64sha256("${var.lambda_source_folder}/${each.value.zip}")

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_iam_role_policy_attachment.lambda_policy_attachment
  ]
}





