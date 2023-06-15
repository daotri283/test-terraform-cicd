# Initialize AWS provider
provider "aws" {
  region     = "ap-southeast-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# Create S3 bucket for input data
resource "aws_s3_bucket" "input_bucket" {
  bucket = "tri-test-bucket-final"
}

# Create S3 bucket for output data
resource "aws_s3_bucket" "output_bucket" {
  bucket = "tri-test-bucket-output"
}

# Zip function code for Lambda deployment
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "lambda_function/"
  output_path = "lambda_function.zip"
}

# Create Lambda function
resource "aws_lambda_function" "data_combiner" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "data_combiner"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  timeout          = 60
  memory_size      = 128
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  environment {
    variables = {
      INPUT_BUCKET  = aws_s3_bucket.input_bucket.id
      OUTPUT_BUCKET = aws_s3_bucket.output_bucket.id
    }
  }
}

# Create IAM role for Lambda execution
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach IAM policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec.name
}
