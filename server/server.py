#!/usr/bin/env python
from apscheduler.scheduler import Scheduler

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from restapi import app, trainer, _dump_classifier

trainer.start()

sched = Scheduler()
sched.start()
sched.add_interval_job(_dump_classifier, minutes=1)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)
IOLoop.instance().start()