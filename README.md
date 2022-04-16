# Mailman3 Exporter for Prometheus 

This prometheus exporter monitors the [mailman3](https://www.mailman.org/) mailing list server. 
Stats are collected using the mailman3 REST API.

## Installing

Download and run the latest binary from the [releases tab](https://github.com/rivmey/exim_exporter/releases/latest). 

```shell script
./mailman3_exporter --mailman3.password=PASS --mailman3.user=USER
```

## Usage

By default, the exporter serves on port `9934` at `/metrics`. 

## Building

```shell script
pip3 install -r requirements.txt
```

## Metrics

See example metrics in [tests](https://github.com/mailman3/mailman_exporter/blob/master/test/update.metrics).

### `mailman3_up`

Whether the main exim daemon is running.

