#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Prometheus mailman3 exporter using rest api's.
    Created by rivimey.
"""

import requests
import argparse
import json
import logging
import re
import sys
import signal
import time
import pprint
from prometheus_client import start_http_server, generate_latest, Gauge, CollectorRegistry
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
exporter = None
MM_API_VERS="3.1"

PROCESSING_TIME = None
class metric_processing_time:
    def __init__(self, name):
        self.start = None
        self.name = name

    def __enter__(self):
        self.start = time.process_time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.process_time() - self.start) * 1000
        logging.debug('Processing %s took %s miliseconds' % (self.name, elapsed))
        PROCESSING_TIME.add_metric([self.name], elapsed)

class MailmanExporter:

    def __init__(self):
        self.web_listen = ""
        self.mailman_address = ""
        self.mailman_user = ""
        self.mailman_password = ""

    def args(self):
        parser = argparse.ArgumentParser(description='Mailman3 Prometheus metrics exporter')
        parser.add_argument('--log-level', default='INFO', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Detail level to log. (default: info)')
        parser.add_argument('-l', '--web.listen', dest='web_listen', type=str, default="localhost:9934", help='HTTPServer metrics listen address')

        parser.add_argument('-m', '--mailman.address', dest='mailman_address', type=str, default="http://localhost:8870", help='Mailman3 Core REST API address')
        parser.add_argument('-u', '--mailman.user', dest='mailman_user', type=str, required=True, help='Mailman3 Core REST API username')
        parser.add_argument('-p', '--mailman.password', dest='mailman_password', type=str, required=True, help='Mailman3 Core REST API password')
        args = parser.parse_args()

        log_format = '[%(asctime)s] %(name)s.%(levelname)s %(threadName)s %(message)s'
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(logging.Formatter(log_format))
        log_level = logging.os.environ.get('LOG_LEVEL', 'INFO')
        log_level = getattr(logging, args.log_level.upper(), log_level.upper() )
        logging.basicConfig(handlers=[log_handler], level=log_level)
        logging.captureWarnings(True)

        self.web_listen = args.web_listen
        self.mailman_address = args.mailman_address
        self.mailman_user = args.mailman_user
        self.mailman_password = args.mailman_password
        url = self.mailman_url("/")
        logging.info("Querying Mailman at URL: <%s>", url)

        return args

    def mailman_url(self, uri=""):
        """Return the URL for the mailman rest service, with the
        optional uri appended. URIs passed in should include an initial '/'.
        """
        return "{}/{}{}".format(self.mailman_address, MM_API_VERS, uri)

    def usercount(self):
        response = { 'status_code': 0 }
        try:
            usrs = {}
            url = self.mailman_url("/users?count=1&page=1")
            response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
            if 200 <= response.status_code < 220:
                usrs = response.json()
        except:
            logging.info("usercount: exception")
            return 500, {}

        logging.debug("usercount: url %s" % response.request.url)
        logging.debug("usercount: content %s" % response.content[:160])
        return response.status_code, usrs

    def versions(self):
        response = { 'status_code': 0, 'request': '' }
        try:
            url = self.mailman_url("/system/versions")
            response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
        except:
            logging.info("versions: exception")
            return 500, {}

        logging.debug("versions: url %s" % response.request.url)
        logging.debug("versions: content %s" % response.content[:160])
        return response.status_code, response

    def domains(self):
        response = { 'status_code': 0 }
        domains = {}
        try:
            url = self.mailman_url("/domains")
            response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
            if 200 <= response.status_code < 220:
                domains = response.json()
        except:
            logging.info("domains: exception")
            return 500, {}

        logging.debug("domains: url %s" % response.request.url)
        logging.debug("domains: content %s" % response.content[:160])
        return response.status_code, domains

    def lists(self):
        response = { 'status_code': 0 }
        lists = {}
        try:
            url = self.mailman_url("/lists")
            response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
            if 200 <= response.status_code < 220:
                lists = response.json()
        except:
            logging.info("lists: exception")
            return 500, {}

        logging.debug("lists: url %s" % response.request.url)
        logging.debug("lists: content %s" % response.content[:160])
        return response.status_code, lists

    def queues(self):
        response = { 'status_code': 0 }
        queues = {}
        try:
            url = self.mailman_url("/queues")
            response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
            if 200 <= response.status_code < 220:
                queues = response.json()
        except:
            logging.info("queues: exception")
            return 500, {}

        logging.debug("queues: url %s" % response.request.url)
        logging.debug("queues: content %s" % response.content[:120])
        return response.status_code, queues


class MailmanCollector(object):

    def __init__(self, exporter):
        self.exporter = exporter
        self.lastcheck = 0

        self.domains_status = 0
        self.domains = []
        self.lists_status = 0
        self.lists = []

    def collect(self):
        global PROCESSING_TIME
        proc_labels = [ 'method', 'up', 'queue', 'domains', 'lists', 'users' ]
        PROCESSING_TIME = GaugeMetricFamily('processing_time_ms', 'Time taken to collect metrics', labels=proc_labels)

        slow_refresh = False
        now = time.monotonic() 
        if now - self.lastcheck > 30:
            logging.debug("do slow_refresh")
            slow_refresh = True
            self.lastcheck = now

        with metric_processing_time('domains'):
            mailman3_domains = GaugeMetricFamily('mailman3_domains', 'Number of configured list domains')
            if slow_refresh:
                self.domains_status, self.domains = self.exporter.domains()
            if 200 <= self.domains_status < 220:
                mailman3_domains.add_metric(['count'], self.domains['total_size'])
            else:
                mailman3_domains.add_metric(['count'], 0)
            yield mailman3_domains

        with metric_processing_time('lists'):
            mailman3_lists = GaugeMetricFamily('mailman3_lists', 'Number of configured lists')
            no_lists = False
            if slow_refresh:
                self.lists_status, self.lists = self.exporter.lists()
            if 200 <= self.lists_status < 220:
                mailman3_lists.add_metric(['count'], self.lists['total_size'])
            else:
                mailman3_lists.add_metric(['count'], 0)
                no_lists = True
            yield mailman3_lists

            mlabels = [ 'list' ]
            if not no_lists:
                for e in self.lists['entries']:
                    logging.debug("members: label %s" % e['fqdn_listname'])
                    mlabels.append(e['fqdn_listname'])
            mailman3_list_members = CounterMetricFamily('mailman3_list_members', 'Count members per list', labels=mlabels)
            if not no_lists:
                for e in self.lists['entries']:
                    logging.debug("members metric %s value %s", e['fqdn_listname'], str(e['member_count']))
                    mailman3_list_members.add_metric([e['fqdn_listname']], value=e['member_count'])
            yield mailman3_list_members

        with metric_processing_time('up'):
            mailman3_up = GaugeMetricFamily('mailman3_up', 'Status of mailman-core; 1 if accessible, 0 otherwise')
            status, resp = self.exporter.versions()
            if 200 <= status < 220:
                mailman3_up.add_metric(['up'], 1)
            else:
                mailman3_up.add_metric(['up'], 0)
            yield mailman3_up

        with metric_processing_time('users'):
            mailman3_users = CounterMetricFamily('mailman3_users', 'Number of list users recorded in mailman-core')
            status, resp = self.exporter.usercount()
            if 200 <= status < 220:
                mailman3_users.add_metric(['count'], resp['total_size'])
            else:
                mailman3_users.add_metric(['count'], 0)
            yield mailman3_users

        with metric_processing_time('queue'):
            qlabels = [ 'queue',
                "archive", "bad", "bounces", "command",
                "digest", "in", "nntp", "out", "pipeline",
                "retry", "shunt", "virgin"
            ]
            mailman3_queue = GaugeMetricFamily('mailman3_queues', 'Queue length for mailman-core internal queues', labels=qlabels)
            mailman3_queue_status = GaugeMetricFamily('mailman3_queues_status', 'HTTP code for queue status request')
            status, resp = self.exporter.queues()
            if 200 <= status < 220:
                for e in resp['entries']:
                    logging.debug("queue metric %s value %s", e['name'], str(e['count']))
                    mailman3_queue.add_metric([e['name']], value=e['count'])
                mailman3_queue_status.add_metric(['status'], value=status)
            else:
                mailman3_queue_status.add_metric(['status'], value=status)
            yield mailman3_queue

        yield PROCESSING_TIME


def index():
    return """
<html><head><title>Mailman3 Prometheus Exporter</title></head>
<body>
<h1>Mailman3 Prometheus Exporter</h1>
<p>Prometheus metrics bridge for the Mailman3 REST API</p>
<p>Visit the metrics page at: <a href="/metrics">/metrics</a>.</p>
</body>
"""

def parse_host_port(listen):
    uri_info = listen.rsplit(r':', 1)
    if len(uri_info) == 0:
        hostname = 'localhost'
        port = 9934
    elif len(uri_info) == 1:
        hostname = uri_info[0]
        port = 9934
    elif len(uri_info) == 2:
        hostname = uri_info[0]
        port = int(uri_info[1])
    else:
        logging.info("Listen address in unexpected form (got '%s')", listen)
        raise ValueError("listen address in unexpected form (got '%s')" % listen)

    if hostname.startswith('['):
        hostname = hostname[1:-1]

    return (hostname, port)

def signal_handler():
    shutdown(1)

def shutdown(code):
    logging.info('Shutting down')
    sys.exit(code)

def main():
    global exporter
    signal.signal(signal.SIGTERM, signal_handler)

    exporter = MailmanExporter()
    cli_args = exporter.args()
    (hostname, port) = parse_host_port(cli_args.web_listen)

    logging.info('Starting server...')
    start_http_server(addr=hostname, port=port, registry=REGISTRY)
    logging.info('Server started on port %s', port)

    REGISTRY.register(MailmanCollector(exporter))
    while True:
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

