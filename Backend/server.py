#!/usr/bin/env python

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from devserver import app, trainer

trainer.start()

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)
IOLoop.instance().start()