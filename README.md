# LocalStack benchmarking with locust

[locust](https://locust.io/) is a "modern load testing framework". We can use this to benchmark LocalStack performance by load testing.

## Getting started

* Start LocalStack with your performance improvements
* Clone this repository and install the development dependencies `python -m pip install .[dev]`

### Testing via the UI

* Start the benchmarking web interface: `locust [--tags <tag>...]` and visit its URL (default: `127.0.0.1:8089`)
* Choose the load testing parameters (e.g. 100 concurrent users at 1 additional user per second)
* Click "Start" and your load testing session will start

When you are happy with your benchmark, visit the [reports page](http://0.0.0.0:8089/?tab=reports) and download the report you are interested in.

### Testing via the command line

* Run the benchmark in headless mode with `locust --headless --users <concurrent users> --spawn-rate <spawn rate> -H http://127.0.0.1:4566 [--run-time <run time>] [--tags <tag>...] [--html <report-file>] [--csv <report-file-prefix>]`
* Either add `--run-time <run time>` to your command line, or Ctrl-C the benchmark to write the report files

## Comparing runs

This repository contains a script that shows a comparison chart for the average 
* requests per second
* p50
* p99

for each csv file passed in on the command line.

For example:
```
python ./compare_runs.py baseline_stats.csv new_feature.csv
```

This opens an interactive plot in your web browser to understand the results.
