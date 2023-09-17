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

```
  # HELP mailman3_domains Number of configured list domains
  # TYPE mailman3_domains gauge
  mailman3_domains 1.0
  # HELP mailman3_lists Number of configured lists
  # TYPE mailman3_lists gauge
  mailman3_lists 8.0
  # HELP mailman3_list_members_total Count members per list
  # TYPE mailman3_list_members_total counter
  mailman3_list_members_total{list="list1@example.com"} 104.0
  mailman3_list_members_total{list="list2@example.com"} 26.0
  mailman3_list_members_total{list="list3@example.com"} 7.0
  mailman3_list_members_total{list="list4@example.com"} 74.0
  mailman3_list_members_total{list="list5@example.com"} 30.0
  mailman3_list_members_total{list="list6@example.com"} 6.0
  mailman3_list_members_total{list="list7@example.com"} 1.0
  mailman3_list_members_total{list="list8@example.com"} 1.0
  # HELP mailman3_up Status of mailman-core; 1 if accessible, 0 otherwise
  # TYPE mailman3_up gauge
  mailman3_up 1.0
  # HELP mailman3_users_total Number of list users recorded in mailman-core
  # TYPE mailman3_users_total counter
  mailman3_users_total 288.0
  # HELP mailman3_queues Queue length for mailman-core internal queues
  # TYPE mailman3_queues gauge
  mailman3_queues{queue="archive"} 10.0
  mailman3_queues{queue="bad"} 0.0
  mailman3_queues{queue="bounces"} 0.0
  mailman3_queues{queue="command"} 0.0
  mailman3_queues{queue="digest"} 0.0
  mailman3_queues{queue="in"} 1.0
  mailman3_queues{queue="nntp"} 0.0
  mailman3_queues{queue="out"} 0.0
  mailman3_queues{queue="pipeline"} 0.0
  mailman3_queues{queue="retry"} 0.0
  mailman3_queues{queue="shunt"} 1.0
  mailman3_queues{queue="virgin"} 0.0
  # HELP processing_time_ms Time taken to collect metrics
  # TYPE processing_time_ms gauge
  processing_time_ms{method="domains"} 0.04233299999967244
  processing_time_ms{method="lists"} 0.22640099999993168
  processing_time_ms{method="up"} 5.324605999999843
  processing_time_ms{method="users"} 7.315147000000355
  processing_time_ms{method="queue"} 3.1242169999998737
```

