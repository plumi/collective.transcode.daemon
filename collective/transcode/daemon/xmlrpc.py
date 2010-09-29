#!/usr/bin/env python
# encoding: utf-8
"""
xmlrpc.py

Created by unweb.me <we@unweb.me>. on 2009-11-02. 
Based on Darksnow ConvertDaemon by Jean-Nicolas Bès <jean.nicolas.bes@darksnow.org>
Copyright (c) 2009 unweb.me

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

"""
$Id$
"""

import os
import xmlrpclib
import urllib
from twisted.internet import reactor
from twisted.web import xmlrpc
from scheduler import Job
from base64 import b64decode, b64encode
from crypto import decrypt, encrypt
import os.path
from urlparse import urlparse
import shutil

def hex(bytes):
    hexbytes = ""
    for c in bytes:
        hexbytes += "%02x" % ord(c)
    return hexbytes

def unhex(hexbytes):
    bytes = ""
    for i in xrange(len(hexbytes)/2):
        bytes+= "%c" % int(hexbytes[i*2:i*2+2])
    return bytes

class XMLRPCConvert(xmlrpc.XMLRPC):
    
    def __init__(self, master):
        self.allowNone = True
        self.master = master

        self.useDateTime = False
    
    def xmlrpc_getAvailableProfiles(self):
        ret = [i['id'] for i in self.master.config['profiles']]
        print ret
        return ret

    def xmlrpc_transcode(self, input, profileId, options, callbackURL, fieldName=''):
        profile = None
        for p in self.master.config['profiles']:
            if profileId == p['id']: 
                profile = p        
        if not profile:
            return "ERROR: Invalid profile %s" % profileId

        try:
            key = decrypt(b64decode(input['key']), self.master.config['secret']) 
            input = eval(key, {"__builtins__":None},{})
            assert input.__class__ is dict
            if profileId == 'dvd':
                input['url'] = input['path']
            else:
                input['url'] = input['url'] + '?' + urllib.urlencode({'key' : b64encode(encrypt(str((input['uid'],input['fieldName'],profileId)),self.master.config['secret']))})
        except Exception, e:
            print "Invalid transcode request: %s" % e
            return "ERROR: Unauthorized"
        
        #if supported_mime_types is empty, we don't check the mime type
        if len(profile['supported_mime_types']) and \
           input['type'] not in profile['supported_mime_types']:
            return "ERROR: Unsupported mimetype %s. Profile %s supports only %s" % (input['type'], profileId, profile['supported_mime_types'])
        output = {}
        job = Job(input, output, profile, options, callbackURL=callbackURL, videofolder=self.master.config['videofolder'], fieldName=fieldName)
        job.defer.addBoth(self.callback, job)
        jobid = self.master.addjob(job)
        if not jobid:
            return "ERROR: couldn't get a jobid"
        if callbackURL:
            return hex(jobid)
        else:
            return job.defer


    def xmlrpc_delete(self, input, options, callbackURL, fieldName=''):
        try:
            key = decrypt(b64decode(input['key']), self.master.config['secret']) 
            input = eval(key, {"__builtins__":None},{})
            assert input.__class__ is dict
            input['url'] = input['url'] + '?' + urllib.urlencode({'key' : b64encode(encrypt(str((input['uid'],input['fieldName'])),self.master.config['secret']))})
        except Exception, e:
            print "Invalid delete request: %s" % e
            return "ERROR: Unauthorized"

         # basic filename checking
        input['path'] = input['path'].replace(' ', '-')
        input['path'] = input['path'].replace('%20', '-')
        input['path'] = input['path'].replace('"', '')
        input['fileName'] = input['fileName'].replace(' ', '-')
        input['fileName'] = input['fileName'].replace('%20', '-')
        input['fileName'] = input['fileName'].replace('"', '')

        parsedURL = urlparse(input['path'])
        hostport = '/'.join(parsedURL[1].split(':'))
        path = self.master.config['videofolder'] + '/' + \
                parsedURL[0] + '/' + \
                hostport + \
                parsedURL[2]
        if os.path.exists(path):
            shutil.rmtree(path)

    def xmlrpc_queueSize(self):
        return self.master.queue.qsize()
    
    def xmlrpc_stat(self, UJId):
        return "ok"
    
    def xmlrpc_stop(self):
        reactor.callLater(0.1, self.master.stop)
        return True
    
    def xmlrpc_cancel(self, UJId):
        self.master.delJob(UJId)
        return True
    
    def callback(self, ret, job):
        print "callback return for jobId %s profile %s is %s" %(b64encode(job.UJId), job.profile['id'],ret)
        cbUrl = job['callbackURL']
        if not cbUrl.endswith('/'):
            cbUrl+='/'
        server = xmlrpclib.Server(cbUrl)
        vals = ret.split()
        key = { 
                  'jobId' : job.UJId,
                  'UID' : job.input['uid'],
                  'fieldName' : job.input['fieldName'], 
                  'profile' : job.profile['id'],
                  'path' : vals[0] == 'SUCCESS' and vals[1] or '',
                  'msg' : ret,
              }
        output = { 'key' : b64encode(encrypt(str(key), self.master.config['secret'])) }
        server.transcode_callback(output)
        return True
