#!/usr/bin/env python

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from client.wsgi import application

http_server = HTTPServer(WSGIContainer(application))
http_server.listen(5050)
IOLoop.instance().start()