import itertools

import boto3
import json
from locust import FastHttpUser, tag, task, events

# TODO: inject locust HTTP client into boto3?
# TODO: use LocalStack `aws_http_client_factory` for an easier API


S3_DATA = "a" * 1024
next_id = itertools.count()

BUCKET_NAME = "test-bucket"
QUEUE_NAME = "test-queue"

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Starting test")
    sqs_client = boto3.client("sqs", endpoint_url="http://localhost:4566")
    sqs_client.create_queue(QueueName=QUEUE_NAME)
    boto3.client("s3", endpoint_url="http://localhost:4566").create_bucket(Bucket=BUCKET_NAME)


class LocalStackUser(FastHttpUser):

    host = "http://127.0.0.1:4566"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = next(next_id)

    @tag("sqs")
    @task
    def send_and_get_message(self):
        self.client.post(
            "/",
            headers={
                "X-Amz-Target": "AmazonSQS.SendMessage",
                "Content-Type": "application/x-amz-json-1.0",
                "X-Amz-Date": "20241007T071721Z",
                "Authorization": "AWS4-HMAC-SHA256 Credential=test/20241007/us-east-1/sqs/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=c9fe61f2ab75e22edabb9bd45aae6ee6e3650b682750e8242b92a63720425324",
            },
            data=json.dumps({
                "QueueUrl": f"http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/{QUEUE_NAME}", "MessageBody": "{}"
                }),
            name="SendMessage",
        )
        response = self.client.post(
            "/",
            headers={
                "X-Amz-Target": "AmazonSQS.ReceiveMessage",
                "Content-Type": "application/x-amz-json-1.0",
                "X-Amz-Date": "20241007T072208Z",
                "Authorization": "AWS4-HMAC-SHA256 Credential=test/20241007/us-east-1/sqs/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=d83d4469f0c11036e8505d575bf1924e9c11830f3f7a373468aa55d144961a7b",
            },
            data=json.dumps({
                "QueueUrl": f"http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/{QUEUE_NAME}",
            }),
            name="ReceiveMessage",
        )
        receipt = response.json()["Messages"][0]["ReceiptHandle"]
        response = self.client.post(
            "/",
            headers={
                "X-Amz-Target": "AmazonSQS.DeleteMessage",
                "Content-Type": "application/x-amz-json-1.0",
                "X-Amz-Date": "20241007T123742Z",
                "Authorization": "AWS4-HMAC-SHA256 Credential=test/20241007/us-east-1/sqs/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=2587550914e23f75cffd374dc3546283e0a4bbdfbfce187401fc8c34f452e623",
            },
            data=json.dumps({
                "QueueUrl": f"http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/{QUEUE_NAME}",
                "ReceiptHandle": f"{receipt}",
            }),
            name="DeleteMessage",
        )

    @tag("s3")
    @task
    def put_and_get_object(self):
        self.client.put(
            f"/{BUCKET_NAME}/test-{self.id}",
            headers={
                "X-Amz-Date": "20241008T122606Z",
                "X-Amz-Content-SHA256": "c5005b56725c985c5a351b9cda5b44b792e72406b0c94bde06a8ba51b85976df",
                "Authorization": "AWS4-HMAC-SHA256 Credential=test/20241008/us-east-1/s3/aws4_request, SignedHeaders=content-md5;host;x-amz-content-sha256;x-amz-date, Signature=dbb0cea05c75425f3cfbd732ad238477818243b6031fe144c1e4baa782024068",
            },
            data=S3_DATA,
            name="PutObject",
        )
        self.client.get(
            f"/{BUCKET_NAME}/test-{self.id}",
            headers={
                "X-Amz-Date": b"20241008T122606Z",
                "X-Amz-Content-SHA256": b"c5005b56725c985c5a351b9cda5b44b792e72406b0c94bde06a8ba51b85976df",
                "Authorization": b"AWS4-HMAC-SHA256 Credential=test/20241008/us-east-1/s3/aws4_request, SignedHeaders=content-md5;host;x-amz-content-sha256;x-amz-date, Signature=dbb0cea05c75425f3cfbd732ad238477818243b6031fe144c1e4baa782024068",
            },
            name="GetObject",
        )
