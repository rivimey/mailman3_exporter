# Mailman3 Exporter for Prometheus 

This prometheus exporter monitors the [mailman3](https://www.mailman.org/) mailing list server. 
Stats are collected using mailman3 core process own REST API and include status, number of lists,
list names, number of users per list, and more.

## Installing

Download and run the latest executable from the [releases tab](https://github.com/rivmey/exim_exporter/releases/latest). 
Alternatively, `git clone` this repository.  Create a virtual environment, e.g.:

```shell script
python3 -m venv .
```

and then install the required packages:

```shell script
bin/pip3 install -r requirements.txt
```

The program can then be run, e.g. by:

```shell script
bin/python3 ./mailman3_exporter.py -p PASS -u USER
```

If python complains packages are missing, check that you are invoking the
program with the correct virtual environment.

## Usage

By default, the exporter serves on port `9934` at `/metrics`. The help message
includes: 

```
mailman\_exporter.py --mailman.user MAILMAN\_USER
                     --mailman.password MAILMAN\_PASSWORD
                     [-l WEB\_LISTEN]
                     [-m MAILMAN\_ADDRESS]
                     [--log-level {debug,info,warning,error,critical}]
```

User and password are not optional.

```
Arguments:
  -h, --help            show this help message and exit
  --log-level {debug,info,warning,error,critical}
                        Detail level to log. (default: info)
  -l WEB\_LISTEN, --web.listen WEB\_LISTEN
                        HTTPServer metrics listen address
  -m MAILMAN\_ADDRESS, --mailman.address MAILMAN\_ADDRESS
                        Mailman3 Core REST API address
  -u MAILMAN\_USER, --mailman.user MAILMAN\_USER
                        Mailman3 Core REST API username
  -p MAILMAN\_PASSWORD, --mailman.password MAILMAN\_PASSWORD
                        Mailman3 Core REST API password
```

## Metrics

See example metrics in [tests](https://github.com/mailman3/mailman_exporter/blob/master/test/update.metrics).
