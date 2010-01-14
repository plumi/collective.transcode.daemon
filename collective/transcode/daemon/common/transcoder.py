#!/usr/bin/env python
# encoding: utf-8
"""
transcoder.py

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

from time import sleep
import re, os
from popen2 import Popen3
from select import select

from xmlreader import ListableClass

class TranscoderConfig(ListableClass):
    def _enter(self):
        self.build


class Transcoder(object):
    
    timeout=      1
    logStrip=     True
    logAll=       False
    logMatch=     False
    logNoMatch=   False
    
    def __init__(self,master=None):
        self.master=master
        logRegex = self.logRegex
        self.logRegex=[]
        for rex, func in logRegex:
            self.logRegex.append((re.compile(rex),func))
    
    def start(self, cmd):
        print "cmd %s" % cmd
        cmdObj = Popen3(cmd, True)
        cmdRet=-1
        while cmdRet == -1:
            cmdRet = cmdObj.poll()
            rfds = select([cmdObj.fromchild, cmdObj.childerr], [], [], self.timeout)[0]
            for fd in rfds:
                line = fd.readline()
                if self.logStrip:
                    line = line.strip()
                    if not line:
                        continue
                if self.logAll:
                    print line
                matched=False
                for rex, funk in self.logRegex:
                    rexRes = rex.search(line)
                    if rexRes:
                        if funk:
                            funk(line, rexRes)
                        matched=True
                if not matched and self.logNoMatch and not self.logAll:
                    print "UNMATCHED"+line
                elif matched and self.logMatch and not self.logAll:
                    print ">",line
        if cmdObj.poll()==-1:
            os.kill(cmdObj.pid, 15)
            for i in xrange(3):
                sleep(1)
                cmdRet=cmdObj.poll()
                if cmdRet>-1:
                    break
            if cmdRet==-1:
                os.kill(cmdObj.pid, 9)
        return cmdRet
    
