# Long Polling with Lambda Event Source Mapping & SQS

## Quickstart

* Start LocalStack inside a Docker container with your performance improvements. The below was used:
```shell
python -m localstack.dev.run -e DNS_ADDRESS=0 -e LS_LOG=WARNING -e SQS_DISABLE_CLOUDWATCH_METRICS=1 -e LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=80
```

* Ensure you're in the `experiments/long_polling_esm_sqs` directory:
```shell
cd experiments/long_polling_esm_sqs
```

* Run the `create_resources.sh` which will create `NUM_RESOURCES` (default `100`) Lambda functions, SQS queues, and Event Source Mappings, connecting each Lambda to an SQS queue.
```shell
./create_resource.sh
```

* Once resources are loaded in, run the Locust benchmark test with the following command:
```shell
locust --headless --users 100 --spawn-rate 2 -H http://127.0.0.1:4566 --run-time 300 --tags "sqs" --html $(date +%F_%H-%M-%S)-report.html -f locustfile.py
```

* Upon test completion, an HTML file will be created (i.e `2025-02-12_16-59-49-report.html`) with generated tables and figures showing LocalStack's test performance.

## Experiment Details

### Comparisons
* Baseline: HEAD of `master` at [`95782dcfa`](https://github.com/localstack/localstack/commit/95782dcfa)
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
* LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT[^1]: `80`

[^1]: Under high volumes, we noticed Lambdas timing out on start-up. While `80` is quite defensive, failures in performance tests are unideal and expensive (skewing results).

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

#### Experiment 1: Batch Size=1000, Batch Window=20s

* Batch Size: `1000`
* Batch Window: `20s`

| Long Polling | # Requests | P(50)   | P(95)   | P(99)    |
|--------------|------------|---------|---------|----------|
| Yes          |   64535    |  370 ms | 740 ms  | 1000 ms  |
| No           |   68355    |  340 ms | 730 ms  | 930 ms   |


#### Experiment 2: Batch Size=10000, Batch Window=300s

* Batch Size: `10000`
* Batch Window: `300s`

| Long Polling | # Requests | P(50)   | P(95)   | P(99)    |
|--------------|------------|---------|---------|----------|
| Yes          |   107023   |  230 ms | 510 ms  | 660 ms   |
| No           |   68355    |  220 ms | 780 ms  | 950 ms   |

#### Experiment 3: Batch Size=10, Batch Window=300s

* Batch Size: `10`
* Batch Window: `300s`

| Long Polling | # Requests | P(50)   | P(95)   | P(99)    |
|--------------|------------|---------|---------|----------|
| Yes          |   107023   |  230 ms | 510 ms  | 660 ms  |
| No           |   68355    |  220 ms | 780 ms  | 950 ms   |