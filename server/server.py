#!/usr/bin/env python
from multiprocessing import Process

from apscheduler.scheduler import Scheduler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from classifier_manager import get_classifier, train_classifier, dump_classifier
from restapi import app


def start():
    classifier = get_classifier()

    trainer = Process(target=train_classifier, args=[classifier])
    trainer.start()

    sched = Scheduler()
    sched.start()
    sched.add_interval_job(dump_classifier, args=[classifier], hours=1)

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()


if __name__ == '__main__':
    start()