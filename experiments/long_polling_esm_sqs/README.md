# Long Polling with Lambda Event Source Mapping & SQS

## Quickstart

* Start LocalStack with your performance improvements. The below was used:
```shell
DNS_ADDRESS=0 LS_LOG=WARNING SQS_DISABLE_CLOUDWATCH_METRICS=1 python -m localstack.runtime.main
```

* Run the `create_resources.sh` which will create `NUM_RESOURCES` (default `100`) Lambda functions, SQS queues, and Event Source Mappings, connecting each Lambda to an SQS queue.
```shell
./create_resource.sh
```

* Once resources are loaded in, run the Locust benchmark test with the following command:
```shell
locust-benchmarking % locust --headless --users 100 --spawn-rate 2 -H http://127.0.0.1:4566 --run-time 300 --tags "sqs" --html $(date +%F_%H-%M-%S)-report.html -f locustfile_boto.py
```

* Upon test completion, an HTML file will be created (i.e `2025-02-12_16-59-49-report.html`) with generated tables and figures showing LocalStack's test performance.

## Experiment Details

### Comparisons
* Baseline: HEAD of `master` at [`bfb17b72`](https://github.com/localstack/localstack/commit/bfb17b723cf9cb0c8c4ca2ef6e232d28518581d0)
* Feature Branch: https://github.com/localstack/localstack/pull/12002

### Measurement
* Test randomly sampled from live SQS queues (with attached ESMs) and did a `SendMessage` with the body `{"foo": "bar"}`.

### Test details:

* Duration: 5 minutes
* Users: `100`
* Spawn rate: 2 per sec

### Hardware

Host Machine Resources:

* OS: `Darwin 23.3.0 arm64`
* CPU: `Apple M3 Pro`
* Cores: `12`
* Memory: `36GB`

Docker Desktop Allocated Resources:

* Cores: `12`
* Memory: `8GB`

### LocalStack Environment:

* SQS CloudWatch Metrics: `DISABLED`
* Log Level: `WARNING`
* DNS Address: `DISABLED`


```shell
LS_LOG=WARNING SQS_DISABLE_CLOUDWATCH_METRICS=1 python -m localstack.runtime.main
```

#### SQS queues
* Count: `100`

#### Lambda functions:
* Count: `100`
* Timeout: `400s`
* Code: [Lambda function `index.py`](./index.py)
        
#### Event source mappings
* Count: `100`
* Batch Size: `1000`
* Batch Window: `20s`

## Results

| Long Polling | N | Avg Requests | Avg RPS | P(50)        | P(95)        | P(99)          |
|--------------|---|--------------|---------|--------------|--------------|----------------|
| No           | 3 |    84,678.67 |  282.26 | 160 - 170 ms | 560 - 860 ms | 1000 - 1500 ms |
| Yes          | 2 |   172,902.50 |  576.34 | 120 - 130 ms | 380 - 510 ms | 540 - 810 ms   |