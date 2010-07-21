Introduction
============
collective.transcode.daemon is an XML-RPC daemon servicing requests for 
transcoding jobs. 

It was initially developed during the Plone Video Sprint that took place 
right after the Plone Conference 2009 in Budapest. It was based on the 
darksnow.convertdaemon code but has evolved a lot since

 * https://svn.atreal.net/public/svn.darksnow.org/ConvertDaemon

It's  currently used for video transcoding in Plumi 3.0 and 3.1 and is a part
of the collective.transcode.* suite for Plone 3.x & 4.x.

 * http://plumi.org
 * http://pypi.python.org/pypi/collective.transcode.star

Even though the only it has only been integrated with Plone, There is nothing Plone
specific the the collective.transcode.daemon package.


Installation
============
The instructions below are for setting up a standalone transcode daemon.

If you want a complete transcoding solution for the Plone CMS use
collective.transcode.star: 

http://pypi.python.org/pypi/collective.transcode.star

Requirements 
~~~~~~~~~~~~
The default transcode scripts require ffmpeg with x264 support and 
ffmpeg2theora.

Has been tested with Python2.4 and Python2.6

Buildout
~~~~~~~~
The best way to install a standalone daemon is to use zc.buildout and the 
buildout.cfg file provided::

    python2.6 bootstrap.py
    ./bin/buildout

Configuration
=============
On buildout.cfg, upon transcodedaemon section, the following settings can be 
configured::

    listen_host = locahost   # IP address or hostname to listen
    listen_port = 8888       # Port to use
    videofolder = transcoded # Path of folder where transcoded videos are stored
    secret = sh4r3dkey       # Secret key shared between daemon and app
    profiles = ...           # A dictionary of supported transcoding profiles

You can change the quality and format of the transcoded files by editing the transcoding
scripts provided in the scripts dir.

Authors
=======
Unweb.me, https://unweb.me
