#!/bin/bash
# Lambda Deployment Script
# This script packages the backend code and updates the Lambda function directly

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_FUNCTION_NAME="music-subscription-app"
echo "=== AWS Music Subscription App - Lambda Deployment ==="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "Function: $LAMBDA_FUNCTION_NAME"
echo ""

# Step 1: Create deployment package
echo "Step 1: Creating Lambda deployment package..."
cd "$(dirname "$0")/../../backend"

# Create a clean directory for packaging
rm -rf lambda_package
mkdir -p lambda_package

# Copy application code
cp -r app lambda_package/
cp lambda_handler.py lambda_package/
cp requirements.txt lambda_package/

# Install dependencies
echo "Installing dependencies..."
pip install \
  --target ./lambda_package \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.10 \
  --only-binary=:all: \
  --upgrade \
  -r requirements.txt

# Create deployment ZIP
echo "Creating deployment package..."
cd lambda_package
zip -r ../lambda_deployment.zip . -q
cd ..
rm -rf lambda_package

echo "Lambda deployment package created: lambda_deployment.zip"
echo "Package size: $(du -h lambda_deployment.zip | cut -f1)"

# Step 2: Upload Lambda code directly
echo ""
echo "Step 2: Uploading Lambda code..."
aws lambda update-function-code \
  --function-name $LAMBDA_FUNCTION_NAME \
  --zip-file fileb://../../backend/lambda_deployment.zip \
  --region $AWS_REGION \
  2>/dev/null || echo "Function may not exist yet"

# Step 3: Get deployment info
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To test the API endpoint:"
echo "  curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/docs"
