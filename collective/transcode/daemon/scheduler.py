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


import time, os, fcntl, signal, socket
from hashlib import sha1 as sha
from Queue import Queue
import urllib
from urlparse import urlparse

from twisted.internet import reactor
from twisted.python import threadable, failure
threadable.init(1)
from twisted.internet.defer import Deferred
import sys, datetime, tempfile
from subprocess import Popen, PIPE, STDOUT

IDLE_CYCLES_LIMIT = 30
SLEEP_CYCLE = 4

def getDuration(lines):
    """ Get the original file's duration by parsing ffmpeg transcode job output"""
    for line in lines:
        if line.find('Duration:') != -1:
            duration = line[line.find('Duration:'):].split(',')[0].split(':')[1:]
            return int(duration[0])*3600+int(duration[1])*60+int(float(duration[2]))
    return 0

def getComplete(lines, duration):
    """ Get ffmpeg transcoding job completion progress, given the duration """
    for line in lines:
        if line.rfind('time=') != -1:
            time = line[line.rfind('time='):].split(' ')[0].split('=')[1].split(':')
            return (int(time[0])*3600 +
                    int(time[1])*60 +
                    int(float(time[2].replace('-','')))
                    )*100/duration


class Job(dict):
    def __init__(self, input, output, profile, options, **kwargs):
        dict.__init__(self)
        self.input = input
        self.output = output
        self.options = options
        self.profile = profile
        self.defer = Deferred()
        self.duration = 0
        self.complete = 0        
        for key,value in kwargs.items():
            self[key] = value

        # basic filename checking
        input['path'] = input['path'].replace(' ', '-')
        input['path'] = input['path'].replace('%20', '-')
        input['path'] = input['path'].replace('%23', '#')
        input['path'] = input['path'].replace('"', '')
        input['fileName'] = input['fileName'].replace(' ', '-')
        input['fileName'] = input['fileName'].replace('%20', '-')
        input['fileName'] = input['fileName'].replace('%23', '#')
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
                job.cmd = job.profile['cmd'] % (url, job.output['path']) 
                print "RUNNING: %s" % job.cmd
                os.umask(0)
                p = Popen(job.cmd.split(' '), stdin=PIPE, stdout=PIPE, 
                          stderr=STDOUT, close_fds=True, preexec_fn = os.setsid)
                fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
                ret = None
                i = 0
                while ret is None:
                    lines = []
                    # wait for process to do stuff
                    time.sleep(SLEEP_CYCLE)

                    # get it's output
                    try:                        
                        lines+=p.stdout.read().split('\r')
                    except:
                        pass
                    try:
                        lines+=p.stderr.read().split('\r')
                    except:
                        pass

                    if job.duration == 0 and lines:
                        job.duration = getDuration(lines)
                        print "duration %s" % job.duration

                    if job.duration:
                        complete = getComplete(lines, job.duration)
                        if complete == job.complete:
                            i+=1
                            print "no transcoding progress for %d cycles" % i
                        else:
                            job.complete = complete
                            i = 0
                        print "%s%% complete" % complete
                    elif lines:
                        print "No duration found in lines: %s" % '\n'.join(lines)
                        
                    if i > IDLE_CYCLES_LIMIT: # if the transcoded has not progressed
                        os.killpg(p.pid, signal.SIGTERM)
                        ret = 1
                        raise Exception("Killed child process that stopped transcoding for more than %d seconds: %s" % (IDLE_CYCLES_LIMIT * SLEEP_CYCLE, job.cmd))
                    ret = p.poll()
                job.complete = 100
                errorMessage = '\n'.join(lines)
            except Exception as e:
                errorMessage = e.message
                print "EXCEPTION %s CAUGHT FOR %r" % (e, job)
                
            print "Transcoder returned", ret, job.output
            
            if ret == 0: 
                retPath = job.output['path']
                if job['callbackURL']:
                    reactor.callFromThread(job.defer.callback, 'SUCCESS ' + 
                                           retPath)
                else:
                    job.defer.callback('SUCCESS ' + retPath)
            else:
                if job['callbackURL']:
                    reactor.callFromThread(job.defer.errback, 
                                           failure.Failure(Exception(errorMessage)))
                else:
                    job.defer.errback('ERROR ' + errorMessage)
           
