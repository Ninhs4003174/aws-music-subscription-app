#!/bin/bash
# Frontend Deployment Script
# This script deploys the frontend to AWS (S3 + CloudFront or EC2)

set -e

AWS_REGION="us-east-1"
S3_BUCKET_NAME="music-subscription-frontend-$(date +%s)"
CLOUDFRONT_ENABLED=${CLOUDFRONT_ENABLED:-true}

echo "=== AWS Music Subscription App - Frontend Deployment ==="
echo "AWS Region: $AWS_REGION"
echo "S3 Bucket: $S3_BUCKET_NAME"
echo "CloudFront: $CLOUDFRONT_ENABLED"
echo ""

# Step 1: Create S3 bucket
echo "Step 1: Creating S3 bucket..."
aws s3 mb s3://$S3_BUCKET_NAME --region $AWS_REGION

# Block public access but allow CloudFront
aws s3api put-bucket-versioning \
  --bucket $S3_BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Step 2: Enable static website hosting
echo "Step 2: Configuring S3 for static website hosting..."
aws s3api put-bucket-website \
  --bucket $S3_BUCKET_NAME \
  --website-configuration '{
    "IndexDocument": {"Suffix": "login.html"},
    "ErrorDocument": {"Key": "login.html"}
  }'

# Step 3: Upload frontend files
echo "Step 3: Uploading frontend files..."
cd "$(dirname "$0")/../../frontend"

# Upload HTML files
for file in *.html; do
  aws s3 cp "$file" s3://$S3_BUCKET_NAME/ \
    --content-type "text/html; charset=utf-8" \
    --region $AWS_REGION
done

# Upload CSS files
if [ -d "css" ]; then
  aws s3 cp css/ s3://$S3_BUCKET_NAME/css/ \
    --recursive \
    --content-type "text/css; charset=utf-8" \
    --region $AWS_REGION
fi

# Upload JS files
if [ -d "js" ]; then
  aws s3 cp js/ s3://$S3_BUCKET_NAME/js/ \
    --recursive \
    --content-type "application/javascript; charset=utf-8" \
    --region $AWS_REGION
fi

echo "Frontend files uploaded to S3"

# Step 4: Create CloudFront distribution (optional)
if [ "$CLOUDFRONT_ENABLED" = "true" ]; then
  echo "Step 4: Creating CloudFront distribution..."
  
  CLOUDFRONT_CONFIG=$(cat << 'EOF'
{
  "CallerReference": "music-app-$(date +%s)",
  "Comment": "Music Subscription App Frontend",
  "DefaultRootObject": "login.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3Origin",
        "DomainName": "S3_BUCKET_DOMAIN",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "TargetOriginId": "S3Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0
  },
  "Enabled": true
}
EOF
)
  
  S3_BUCKET_DOMAIN="$S3_BUCKET_NAME.s3-website-$AWS_REGION.amazonaws.com"
  CLOUDFRONT_CONFIG=$(echo "$CLOUDFRONT_CONFIG" | sed "s|S3_BUCKET_DOMAIN|$S3_BUCKET_DOMAIN|g" | sed "s|\$(date +%s)|$(date +%s)|g")
  
  DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "$CLOUDFRONT_CONFIG" \
    --region $AWS_REGION \
    --query 'Distribution.Id' \
    --output text)
  
  echo "CloudFront distribution created: $DISTRIBUTION_ID"
fi

# Step 5: Output deployment info
echo ""
echo "=== Deployment Complete ==="
echo "S3 Bucket: $S3_BUCKET_NAME"
echo ""
echo "Frontend URLs:"
echo "  S3 Website: http://$S3_BUCKET_NAME.s3-website-$AWS_REGION.amazonaws.com"
if [ "$CLOUDFRONT_ENABLED" = "true" ]; then
  echo "  CloudFront: https://$DISTRIBUTION_ID.cloudfront.net"
fi
echo ""
echo "To update frontend files, use:"
echo "  aws s3 sync ./frontend s3://$S3_BUCKET_NAME --exclude '.git/*' --region $AWS_REGION"
