#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Binux <roy@binux.me>

import argparse
import sys
import logging
import tornado.log
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.httpserver import HTTPServer

import config
from web.app import Application
from worker import MainWorker

if __name__ == "__main__":
    # init logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if config.debug else logging.INFO)
    channel = logging.StreamHandler(sys.stdout)
    channel.setFormatter(tornado.log.LogFormatter())
    logger.addHandler(channel)

    if not config.debug:
        channel = logging.StreamHandler(sys.stderr)
        channel.setFormatter(tornado.log.LogFormatter())
        channel.setLevel(logging.WARNING)
        logger.addHandler(channel)

    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument('-p', type=int, help='port', default=config.port)
    argumentParser.add_argument('-b', help='bind IP address', default=config.bind)
    arguments = argumentParser.parse_args()
    port = arguments.p
    bind = arguments.b

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(port, bind)
    http_server.start()

    worker = MainWorker()
    io_loop = IOLoop.instance()
    PeriodicCallback(worker, config.check_task_loop, io_loop).start()
    worker()

    logging.info("http server started on %s:%s", bind, port)
    IOLoop.instance().start()
