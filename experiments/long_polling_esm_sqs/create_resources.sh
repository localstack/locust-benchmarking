#!/bin/bash

# Number of resource sets to create
DEFAULT_NUM_RESOURCES=100
NUM_RESOURCES=${1:-$DEFAULT_NUM_RESOURCES}

echo "Creating ${NUM_RESOURCES} resource sets..."

for i in $(seq 1 $NUM_RESOURCES); do
    # Create SQS queue with identifier
    awslocal sqs create-queue \
        --queue-name "localstack-src-queue-${i}" > /dev/null
    
    # Create Lambda function with identifier
    awslocal lambda create-function \
        --function-name "localstack-esm-function-${i}" \
        --runtime python3.12 \
        --zip-file fileb://function.zip \
        --handler index.handler \
        --timeout 400 \
        --role arn:aws:iam::000000000000:role/lambda-role > /dev/null

    # Create event source mapping with identifier
    awslocal lambda create-event-source-mapping \
        --function-name "localstack-esm-function-${i}" \
        --batch-size 1000 \
        --maximum-batching-window-in-seconds 20 \
        --event-source-arn "arn:aws:sqs:us-east-1:000000000000:localstack-src-queue-${i}" > /dev/null
done

echo "All resources created successfully"