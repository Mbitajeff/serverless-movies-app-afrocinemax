resource "aws_dynamodb_table" "movies_table" {
  name         = "Movies"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "movies"

  attribute {
    name = "movies"
    type = "S"
  }
}