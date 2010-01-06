#!/usr/bin/env python
# encoding: utf-8
"""
scheduler.py

Created by unweb.me <we@unweb.me>. on 2009-11-02. 
Based on Darksnow ConvertDaemon by Jean-Nicolas Bès <jean.nicolas.bes@darksnow.org>

"""

#
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


import time, os
from sha import sha

from twisted.internet import reactor
from twisted.python import threadable
threadable.init(1)
from twisted.internet.defer import Deferred

from twisted.python.timeoutqueue import TimeoutQueue

from utils import systemOut
import urllib

class Job(dict):
    def __init__(self, input, output, profile, options, **kwargs):
        dict.__init__(self)
        self.input=input
        self.output=output
        self.options=options
        self.profile=profile
        self.defer = Deferred()
        for key,value in kwargs.items():
            self[key]=value
    
    def __repr__(self):
        return "<Job input=%r ouput=%r options=%r %s" % (
            self.input,
            self.output,
            self.options,
            dict.__repr__(self),
        )

class JobSched:
  
    def __init__(self):
        self.queue=TimeoutQueue()
        self.job={}
    
    def genUJId(self):
        return sha(str(time.time())).digest()
    
    def addjob(self,job):
        #print "Scheduler addJob", job
        
        UJId=self.genUJId()
        self.job[UJId]=job
        job.UJId=UJId
        self.queue.put(job)
        return UJId
    
    def delJob(UJId):
        del self.job[UJId]
    
    def run(self):
        import imp
        config = imp.load_source('config',self.rel("config.py"))
        self.host = config.listen_host
        self.port = config.listen_port

        print "Scheduler thread running"
        self.running=True
        while self.running:
            job = self.queue.get()
            print "New job"
            if job is None:
                break
            if job.UJId not in self.job:
                print "ERROR the job doesn't exist"
                continue
            try:
                print "DOWNLOADING %s" % job.input['path']
                (filename, response) = urllib.urlretrieve(job.input['path'])
                #TODO - check file was retrieved successfully
                job.cmd = job.profile['cmd'] % (filename, job.output['path'])
                #TODO - make this nicer with caching (needs hashing on both side)

                print "RUNNING: %s" % job.cmd
                ret = os.system(job.cmd)
                os.remove(filename)
            except Exception, e:
                ret = "%s" % e
                print "EXCEPTION %s CAUGHT FOR %r" % (ret, job)
            print "Transcoder returned", ret, job.output
       
            if ret == 0: 
                retPath = job.output['path']
                print retPath
                reactor.callFromThread(job.defer.callback, 'SUCCESS ' + retPath)
            else:
                #TODO - make more useful message
                reactor.callFromThread(job.defer.errback, 'FAIL %d' % ret)
            

