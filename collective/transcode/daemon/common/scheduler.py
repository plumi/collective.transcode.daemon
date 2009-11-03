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


import time
from sha import sha

from twisted.internet import reactor
from twisted.python import threadable
threadable.init(1)
from twisted.internet.defer import Deferred

from twisted.python.timeoutqueue import TimeoutQueue

from utils import systemOut

class Job(dict):
    def __init__(self, input, output, options, **kwargs):
        dict.__init__(self)
        self.input=input
        self.output=output
        self.options=options
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
        #trans = self.getmimeconv(job.input['type'], job.output['type'])
        #if not trans:
        #    print "Transcoding not available from %s to %s." % (
        #        job.input['type'],
        #        job.output['type']
        #        )
        #    return None
        #job.trans = trans
        UJId=self.genUJId()
        self.job[UJId]=job
        job.UJId=UJId
        self.queue.put(job)
        return UJId
    
    def delJob(UJId):
        del self.job[UJId]
    
    def run(self):
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
                ret = self.transcoder[job.trans].transcode(job)
            except Exception, e:
                ret = "%s" % e
                print "EXCEPTION %s CATCHED FOR %r" % (ret, job)
            #print "Transcoder returned", ret
            if ret and getattr(job, 'url', None):
                reactor.callFromThread(job.defer.errback, ret)
            else:
                reactor.callFromThread(job.defer.callback, ret)
  

