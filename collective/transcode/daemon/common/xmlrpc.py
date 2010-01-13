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
from urlparse import urlparse
from twisted.internet import reactor
from twisted.web2 import xmlrpc
from scheduler import Job

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
    
    def xmlrpc_getAvailableProfiles(self, request):
        ret = [i['id'] for i in self.master.config['profiles']]
        print ret
        return ret

    def xmlrpc_convert(self,  request, input, profileId, options, callbackURL):
        videofolder = self.master.config['videofolder']

        #This cleans up unsavoury characters from the path name. A video coming
        #from a URL such as https://local-server:9080/plone/foo/bar will
        #get stored in a directory .../https/local-server/9080/plone/foo/bar/...
        parsedURL = urlparse(input['path'])
        hostport = '/'.join(parsedURL[1].split(':'))
        path = videofolder + '/' + \
                parsedURL[0] + '/' + \
                hostport + \
                parsedURL[2] + '/' + \
                profileId

        #grabs the basename of the file: http://foo/bar/baz.foo.avi would
        #yield baz.foo
        basename = '.'.join(input['path'].split('/')[-1].split('.')[:-1])

        try:
            os.makedirs(path)
        except:
            pass        
        profile = None
        for p in self.master.config['profiles']:
            if profileId == p['id']: profile = p        
        if not profile:
            return "ERROR: Invalid profile %s" % profileId
        outFile = path + '/' + basename + '.' + profile['output_extension']
        output = dict(path=outFile,type=profile['output_mime_type'])
        
        #if supported_mime_types is empty, we don't check the mime type
        if len(profile['supported_mime_types']) and \
           input['type'] not in profile['supported_mime_types']:
            return "ERROR: Unsupported mimetype %s. Profile %s supports only %s" % (input['type'], profileId, profile['supported_mime_types'])
        job = Job(input, output, profile, options, callbackURL=callbackURL)
        job.defer.addBoth(self.callback, job)
#        job.defer.addErrback(self.callback, job)
        jobid = self.master.addjob(job)
        if not jobid:
            return "ERROR couldn't get a jobid"
        if callbackURL:
            return hex(jobid)
        else:
            return job.defer
    
    def xmlrpc_stat(self, request, UJId):
        return "ok"
    
    def xmlrpc_stop(self, request):
        reactor.callLater(0.1, self.master.stop)
        return True
    
    def xmlrpc_cancel(self, request, UJId):
        self.master.delJob(UJId)
        return True
    
    def callback(self, ret, job):
        print "called back plone"
        print "callbackURL =",job['callbackURL']
        print "callback return for profile %s is %s" %(job.profile['id'],ret)
        server=xmlrpclib.Server(job['callbackURL'])
        vals = ret.split()
        if vals[0] == 'SUCCESS':
            server.conv_done_xmlrpc(0, 'SUCCESS', job.profile['id'], vals[1])
        else:
            server.conv_done_xmlrpc(vals[1], vals[0], job.profile['id'], '')
        return True

#    def errback(self, ret, job):
#        print "errored back!"
#        print "callbackURL =",job['callbackURL']
#        server=xmlrpclib.Server(job['callbackURL'])
#        server.conv_done_xmlrpc(ret)
#        return True
#
