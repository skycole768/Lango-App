
resource "aws_dynamodb_table" "lango_table" {
    name           = "LangoApp"
    billing_mode   = "PAY_PER_REQUEST"
    hash_key       = "PK"
    range_key = "SK"

    attribute {
        name = "PK"
        type = "S"
    }
    
    attribute {
        name = "SK"
        type = "S"
    }

    attribute {
        name = "username"
        type = "S"
    }

    global_secondary_index {
        name            = "UsernameIndex"
        hash_key        = "username"
        projection_type = "ALL"
    }

    tags = {
        Name        = var.dynamodb_table_name
        Environment = var.stage_name
    }
  
}