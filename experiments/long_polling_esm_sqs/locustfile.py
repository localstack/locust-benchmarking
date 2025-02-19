import boto3
import time
from locust import User, task, constant, events, tag
import random
import json

import itertools

next_id = itertools.count()

class BotoClient:
    def __init__(self):
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
            endpoint_url="http://localhost:4566" 
        )


    def send(self, queue_url, message_body):

        request_meta = {
            "request_type": "send message",
            "name": "SQS",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        start_perf_counter = time.perf_counter()

        try:
            self.sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)
        except Exception as e:
            request_meta['exception'] = e

        request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000

        events.request.fire(**request_meta)

class BotoUser(User):
    abstract = True

    def __init__(self, env):
        super().__init__(env)
        self.client = BotoClient()


class LocalStackUser(BotoUser):

    host = "http://localhost:4566"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = next(next_id)
        
        resp = self.client.sqs_client.list_queues()
        self.queue_urls = resp.get("QueueUrls", [])

    @tag("sqs")
    @task
    def send_request(self):
        queue_url = random.choice(self.queue_urls)
        self.client.send(queue_url, '{"foo": "bar"}')