#!/bin/bash
# ECS Deployment Script
# This script builds the Docker image, pushes to ECR, and deploys to ECS Fargate

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="music-subscription-app"
ECS_CLUSTER_NAME="music-subscription-cluster"
ECS_SERVICE_NAME="music-subscription-service"
IMAGE_TAG="latest"

echo "=== AWS Music Subscription App - ECS Deployment ==="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPOSITORY_NAME"
echo ""

# Step 1: Create ECR Repository (if not exists)
echo "Step 1: Creating ECR repository..."
aws ecr create-repository \
  --repository-name $ECR_REPOSITORY_NAME \
  --region $AWS_REGION \
  --tags "Key=Project,Value=MusicSubscriptionApp" \
  2>/dev/null || echo "Repository already exists"

# Step 2: Login to ECR
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build Docker image
echo "Step 3: Building Docker image..."
cd "$(dirname "$0")/../../backend"
docker build \
  --platform linux/amd64 \
  --tag $ECR_REPOSITORY_NAME:$IMAGE_TAG \
  --tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG \
  .

# Step 4: Push to ECR
echo "Step 4: Pushing image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Step 5: Create ECS Cluster (if not exists)
echo "Step 5: Creating ECS cluster..."
aws ecs create-cluster \
  --cluster-name $ECS_CLUSTER_NAME \
  --region $AWS_REGION \
  2>/dev/null || echo "Cluster already exists"

# Step 6: Create CloudWatch Log Group
echo "Step 6: Creating CloudWatch log group..."
aws logs create-log-group \
  --log-group-name /ecs/music-subscription-app \
  --region $AWS_REGION \
  2>/dev/null || echo "Log group already exists"

# Step 7: Register Task Definition
echo "Step 7: Registering task definition..."
cd "$(dirname "$0")"
TASK_DEF=$(cat task-definition.json | \
  sed "s|ACCOUNT_ID|$AWS_ACCOUNT_ID|g" | \
  sed "s|us-east-1|$AWS_REGION|g")
echo "$TASK_DEF" > task-definition-temp.json
aws ecs register-task-definition \
  --cli-input-json file://task-definition-temp.json \
  --region $AWS_REGION
rm task-definition-temp.json

# Step 8: Create or Update ECS Service
echo "Step 8: Setting up ECS service..."
TASK_DEF_ARN="arn:aws:ecs:$AWS_REGION:$AWS_ACCOUNT_ID:task-definition/music-subscription-app:1"

SERVICE_EXISTS=$(aws ecs describe-services \
  --cluster $ECS_CLUSTER_NAME \
  --services $ECS_SERVICE_NAME \
  --region $AWS_REGION \
  --query 'services[0].serviceName' \
  --output text 2>/dev/null || echo "NONE")

if [ "$SERVICE_EXISTS" = "NONE" ] || [ -z "$SERVICE_EXISTS" ]; then
  echo "Creating new ECS service..."
  # Note: You'll need to replace SUBNET_IDS and SECURITY_GROUP_IDS
  aws ecs create-service \
    --cluster $ECS_CLUSTER_NAME \
    --service-name $ECS_SERVICE_NAME \
    --task-definition music-subscription-app \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:targetgroup/music-app/xxxxx,containerName=backend,containerPort=8000 \
    --region $AWS_REGION
else
  echo "Updating existing ECS service..."
  aws ecs update-service \
    --cluster $ECS_CLUSTER_NAME \
    --service $ECS_SERVICE_NAME \
    --task-definition music-subscription-app \
    --region $AWS_REGION
fi

echo ""
echo "=== Deployment Complete ==="
echo "ECR Image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"
echo "ECS Cluster: $ECS_CLUSTER_NAME"
echo "ECS Service: $ECS_SERVICE_NAME"
echo ""
echo "To check service status:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --region $AWS_REGION"
