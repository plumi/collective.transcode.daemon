from collective.transcode.daemon import config
from collective.transcode.daemon.crypto import decrypt, encrypt
from collective.transcode.daemon.scheduler import JobSched
from collective.transcode.daemon.xmlrpc import XMLRPCConvert

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.application import service
import xmlrpclib
from time import sleep
from base64 import b64encode
from base64 import b64encode, b64decode
import os

class TranscodeDaemonTestCase(unittest.TestCase):
    def setUp(self):
        self.sched = JobSched()
        self.sched.config = {}
        self.sched.config['profiles'] = eval(config.profiles)
        self.sched.config['listen_host'] = config.listen_host
        self.sched.config['listen_port'] = config.listen_port
        self.sched.config['videofolder'] = config.videofolder
        self.sched.config['secret'] = config.secret        
        self.server = XMLRPCConvert(self.sched)
            
    def test_profiles(self):
        daemonProfiles = self.server.xmlrpc_getAvailableProfiles()
        self.assertEqual(daemonProfiles, [p['id'] for p in eval(config.profiles)])

    def test_transcode(self, profiles = None):
        if not profiles:
            profiles = self.server.xmlrpc_getAvailableProfiles()
            profile = profiles[0]
            os.chdir('..')
        else:
            profile = profiles[0]
        options = dict()
        filePath = 'path'
        fileUrl = 'http://www.engagemedia.org/Members/emnews/videos/wikileaks_parody.mp4/@@download/video_file/wikileaks_parody.mp4'
        fileName = 'wikileaks_parody.mp4'
        UID = '123'
        input = {
                  'path' : filePath,
                  'url' : fileUrl,
                  'type' : 'video/mp4',
                  'fieldName' : '',
                  'fileName' : fileName,
                  'uid' : UID,
                }
        input = {'key':b64encode(encrypt(str(input), config.secret))}
        job = self.server.xmlrpc_transcode(input, profile, options, False)
        def checkResult(info):
            result = eval(decrypt(b64decode(info['key']), config.secret), {"__builtins__":None},{})
            print result
            self.sched.running = False
            assert 'SUCCESS' in result['msg']
            if len(profiles)>1:
                self.test_transcode(profiles[1:])
        job.addCallback(checkResult)
        job.addErrback(checkResult)
        self.sched.run()

        