
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
    for_each = toset(var.lambda_names)

    alarm_name          = "Lango-${each.key}-Errors"
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods  = 1
    metric_name         = "Errors"
    namespace           = "AWS/Lambda"
    actions_enabled = true
    period              = 60
    statistic           = "Sum"
    treat_missing_data = "notBreaching"
    threshold           = 1
    alarm_description   = "Alarm for ${each.key} function errors"
    
    dimensions = {
        FunctionName = each.key
    }
    
    tags = {
        Project     = "Lango"
        Environment = "dev"
        LambdaName  = each.key
    }
}
