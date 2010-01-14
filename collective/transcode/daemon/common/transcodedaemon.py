#!/usr/bin/env python
# encoding: utf-8
"""
transcodedaemon.py

Created by unweb.me <we@unweb.me> on 2009-11-01.
Based on Darksnow ConvertDaemon by Jean-Nicolas Bès <jean.nicolas.bes@darksnow.org>
Copyright (c) 2009 unweb.me. 

# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""

import time

from twisted.application import strports
from twisted.web2 import server, http, resource, channel, static
from twisted.web2 import http_headers, responsecode

from twisted.internet import reactor

from collective.transcode.daemon.common.xmlrpc import XMLRPCConvert

from collective.transcode.daemon.common.scheduler import JobSched
from twisted.application import service

from twisted.web2.stream import readIntoFile

import os
import tempfile

application = service.Application("TranscodeDaemon")

class TranscodeWebRoot(resource.Resource):
    addSlash = True
    
    def filewritten(self, rval, request, tmpfile):
        contenttype = http_headers.MimeType('text', 'plain', charset= "utf-8")
        return http.Response(responsecode.OK,
                {'last-modified': time.time(),
                 'etag': http_headers.ETag(str(hash("OK\r\n"))),
                 'content-type': contenttype,},
                "OK\r\n")

    def error_while_writing(self, err, request):
        contenttype = http_headers.MimeType('text', 'plain', charset= "utf-8")
        return http.Response(responsecode.INTERNAL_SERVER_ERROR,
                             {'last-modified': time.time(),
                              'etag': http_headers.ETag(str(hash("NOT GOOD\r\n"))),
                              'content-type': contenttype,},
                             "NOT GOOD\r\n")

    def http_POST(self, request):
        tmpfile = tempfile.NamedTemporaryFile()
        ofd = os.fdopen(os.dup(tmpfile.file.fileno()), 'wb+')
        defer = readIntoFile(request.stream, ofd)
        defer.addCallback(self.filewritten, request, tmpfile)
        return defer
    
    def render(self, request):
        contenttype = http_headers.MimeType('text', 'plain', charset= "utf-8")
        return http.Response(responsecode.OK,
                {'last-modified': time.time(),
                 'etag': http_headers.ETag(str(hash("OK\r\n"))),
                 'content-type': contenttype,},
                "OK\r\n")


    

class TranscodeDaemon(JobSched):

    @property
    def root(self):
        return os.environ["TRANSCODEDAEMON_ROOT"]
    
    def rel(self, path):
        return os.path.join(self.root, path.lstrip('/'))
    
    def __init__(self, application):
        print "Initializing"
        JobSched.__init__(self)
        
        self.transcoder={}

        import imp
        config = imp.load_source('config',self.rel("config.py"))
        self.config = {}
        self.config['profiles'] = eval(config.profiles)
        self.config['listen_host'] = config.listen_host
        self.config['listen_port'] = config.listen_port
        self.config['videofolder'] = config.videofolder

        self.launchHttp(application)
        reactor.callInThread(self.run)
        print "Launched TranscodeDaemon scheduler thread...."
    
    
    def launchHttp(self, application):
        root = TranscodeWebRoot()
        root.putChild('RPC2', XMLRPCConvert(self))
        root.putChild(self.config['videofolder'],static.File(self.config['videofolder']))
        site = server.Site(root)
        
        httpchan = channel.HTTPFactory(site)
        thyStopFact = httpchan.stopFactory
        mystop = self.stop
        def myStopFact():
            thyStopFact()
            self.stop(stopReactor=False)
        httpchan.stopFactory = myStopFact
        
        host = self.config['listen_host'].encode('ascii')
        port = self.config['listen_port'].encode('ascii')
        
        s = strports.service('tcp:%s:interface=%s' % (port, host), httpchan)
        s.setServiceParent(application)
        print "Launched http channel"
  
    def stop(self, stopReactor = True):
        self.running=False
        self.queue.put(None)
        if stopReactor:
            reactor.stop()
        print "reactor stopped"
        for trans in self.transcoder.keys():
            del self.transcoder[trans]
    
    def __del__(self):
        if self.running:
            self.stop()

TranscodeDaemon(application)




