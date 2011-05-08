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
from hashlib import sha1 as sha
from Queue import Queue
import urllib
from urlparse import urlparse

from twisted.internet import reactor
from twisted.python import threadable
threadable.init(1)
from twisted.internet.defer import Deferred
import sys, subprocess, datetime, tempfile


class Job(dict):
    def __init__(self, input, output, profile, options, **kwargs):
        dict.__init__(self)
        self.input = input
        self.output = output
        self.options = options
        self.profile = profile
        self.defer = Deferred()
        for key,value in kwargs.items():
            self[key] = value

        # basic filename checking
        input['path'] = input['path'].replace(' ', '-')
        input['path'] = input['path'].replace('%20', '-')
        input['path'] = input['path'].replace('"', '')
        input['fileName'] = input['fileName'].replace(' ', '-')
        input['fileName'] = input['fileName'].replace('%20', '-')
        input['fileName'] = input['fileName'].replace('"', '')

        #This cleans up unsavoury characters from the path name. A video coming
        #from a URL such as https://local-server:9080/plone/foo/bar will
        #get stored in a directory .../https/local-server/9080/plone/foo/bar/...
        parsedURL = urlparse(self.input['path'])
        hostport = '/'.join(parsedURL[1].split(':'))
        if input['fieldName']:
            field = '%s/' % input['fieldName']
        else:
            field = ''
        path = self['videofolder'] + '/' + \
                parsedURL[0] + '/' + \
                hostport + \
                parsedURL[2] + '/' + \
                field + self.profile['id']
        try:
            os.umask(0)
            os.makedirs(path)
        except:
            pass

        #grabs the basename of the file
        fileName = input.get('fileName', None) or input['path'].split('/')[-1]
        basename = '.'.join(fileName.split('.')[:-1]) or fileName
        outFile = path + '/' + basename + '.' + profile['output_extension']
        self.output = dict(path = outFile, type = profile['output_mime_type'])
                
    def __repr__(self):
        return "<Job input=%r ouput=%r options=%r %s" % (
            self.input,
            self.output,
            self.options,
            dict.__repr__(self),
        )

class JobSched:
  
    def __init__(self):
        self.queue = Queue()
        self.job = {}
    
    def genUJId(self):
        return sha(str(time.time())).digest()
    
    def addjob(self,job):
        UJId = self.genUJId()
        self.job[UJId] = job
        job.UJId = UJId
        self.queue.put(job)
        return UJId
    
    def delJob(UJId):
        del self.job[UJId]
    
    def run(self):
        print "Scheduler thread running"
        self.running = True
        while self.running:
            try:
                job = self.queue.get(block=True, timeout=5)
            except:
                continue
            if job is None or job.UJId not in self.job:
                print "ERROR the job doesn't exist"
                continue

            print "New job"
            url = job.input['url']

            ret = 1

            try:
                print "DOWNLOADING %s" % url
                (filename, response) = urllib.urlretrieve(url) 
                #TODO - check file was retrieved successfully
                job.cmd = job.profile['cmd'] % (filename, job.output['path']) 
                print "RUNNING: %s" % job.cmd
                os.umask(0)
                ret = os.system(job.cmd)
                os.remove(filename)
            except Exception, e:
                ret = "%s" % e
                print "EXCEPTION %s CAUGHT FOR %r" % (ret, job)
            print "Transcoder returned", ret, job.output
 
            if ret == 0: 
                retPath = job.output['path']
                reactor.callFromThread(job.defer.callback, 'SUCCESS ' + retPath)
            else:
                #TODO - make more useful message
                reactor.callFromThread(job.defer.errback, 'FAIL %s' % ret)
           
