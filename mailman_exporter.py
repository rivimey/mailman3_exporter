#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Prometheus mailman3 exporter using rest api's.
    Created by rivimey.
"""

import requests
import argparse
import json
import re
from flask import Flask, Response
from prometheus_client import generate_latest, Gauge, CollectorRegistry
from prometheus_client.core import GaugeMetricFamily

app = Flask(__name__)
exporter = None
MM_API_VERS="3.1"
_DEBUG = False

class MailmanExporter:

    def __init__(self):
        self.REGISTRY = CollectorRegistry(auto_describe=False)
        self.mailman3_up = Gauge('mailman3_up', 'Status of mailman-core; 1 if accessible, 0 otherwise', registry=self.REGISTRY)
        self.mailman3_queue = GaugeMetricFamily('mailman3_queues', 'Queue length for mailman-core')
        # TODO: needed but this doesn't work.
        #self.REGISTRY.register(self.mailman3_queue)


    def args(self):
        parser = argparse.ArgumentParser(description='Mailman3 Prometheus metrics exporter')
        #parser.add_argument('-c', '--config', dest='config', type=str, help='Pass in a configuration file')
        parser.add_argument('-d', '--debug', dest='debug', type=bool, help='Enable debug output')
        parser.add_argument('-l', '--web.listen', dest='web_listen', type=str, default="localhost:9934", help='HTTPServer listen address')

        parser.add_argument('-m', '--mailman.address', dest='mailman_address', type=str, default="http://localhost:8870", help='Mailman3 Core REST API address')
        parser.add_argument('-u', '--mailman.user', dest='mailman_user', type=str, required=True, help='Mailman3 Core REST API username')
        parser.add_argument('-p', '--mailman.password', dest='mailman_password', type=str, required=True, help='Mailman3 Core REST API password')

        args = parser.parse_args()
        self.web_listen = args.web_listen
        global _DEBUG
        _DEBUG = args.debug
        self.mailman_address = args.mailman_address
        self.mailman_user = args.mailman_user
        self.mailman_password = args.mailman_password
        if _DEBUG:
            url = self.mailman_url("/")
            print("mailman URL: %s" % url)

        return args

    def mailman_url(self, uri=""):
        """Return the URL for the mailman rest service, with the
        optional uri appended. URIs passed in should include an initial '/'.
        """
        return "{}/{}{}".format(self.mailman_address, MM_API_VERS, uri)

    def versions(self):
        url = self.mailman_url("/system/versions")
        response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
        if _DEBUG:
            print("versions: url %s" % response.request.url)
            print("versions: content %s" % response.content)
        return response

    def queues(self):
        url = self.mailman_url("/queues")
        response = requests.get(url, auth=(self.mailman_user, self.mailman_password))
        if _DEBUG:
            print("queues: url %s" % response.request.url)
            print("queues: content %s" % response.content)
        return response

    def collect(self):
        resp = self.versions()
        if 200 <= resp.status_code < 220:
            self.mailman3_up.inc()
        yield self.mailman3_up

        resp = self.queues()
        if 200 <= resp.status_code < 220:
            qlist = resp.json()
            qinfo = {}
            for e in qlist:
                self.mailman3_queue.add_metric([e.name], value=e.count)
        yield self.mailman3_queue


@app.route("/")
def index():
    return """
<html><head><title>Mailman3 Prometheus Exporter</title></head>
<body>
<h1>Mailman3 Prometheus Exporter</h1>
<p>Prometheus metrics bridge for the Mailman3 REST API</p>
<p>Visit the metrics page at: <a href="/metrics">/metrics</a>.</p>
</body>
"""

@app.route("/metrics")
def mailman3Response():
    global exporter
    exporter.collect()
    return Response(generate_latest(exporter.REGISTRY), mimetype="text/plain")


def parse_host_port(listen):
    uri_info = re.split(r':', listen)
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
        raise ValueError("listen address unexpected form (got '%s')" % listen)

    return (hostname, port)

def main():
    global exporter
    exporter = MailmanExporter()
    cli_args = exporter.args()
    (hostname, port) = parse_host_port(cli_args.web_listen)
    app.run(host=hostname, port=port, use_reloader=False)


if __name__ == '__main__':
    main()

