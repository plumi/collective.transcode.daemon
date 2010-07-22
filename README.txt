Introduction
============
collective.transcode.daemon is an XML-RPC daemon servicing requests for 
transcoding jobs. 

It was initially developed during the Plone Video Sprint that took place 
right after the Plone Conference 2009 in Budapest. It was based on the 
darksnow.convertdaemon code but has evolved a lot since

- https://svn.atreal.net/public/svn.darksnow.org/ConvertDaemon

It's  currently used for video transcoding in Plumi 3.0 and 3.1 and is a part
of the collective.transcode.* suite for Plone 3.x & 4.x.

- http://plumi.org
- http://pypi.python.org/pypi/collective.transcode.star

Requirements
------------
Apart from what is assembled by the buildout, the following dependencies must
be installed manually for the transcoding scripts to work:

- ffmpeg with x264 support
- ffmpeg2theora

The daemon has been tested with Python2.4 and Python2.6.

Installation
------------
The instructions below are for setting up a standalone transcode daemon.

If you want a complete transcoding solution for the Plone CMS use
collective.transcode.star

The best way to install a standalone daemon is to use zc.buildout and the
buildout.cfg file provided
::

    python2.6 bootstrap.py
    ./bin/buildout
    ...
    ./bin/transcodedaemon fg
    Initializing
    Launched http channel
    Launched TranscodeDaemon scheduler thread....

Configuration
-------------
You can edit the following options in buildout.cfg:
::

    listen_host
        hostname to listen

    listen_port
        port to use

    videofolder
        relative path of folder where transcoded videos are stored

    secret
        a secret shared key used for authentication and encryption 

    profiles
        a python list of dicts specifying the supported transcoding profiles
 
Don't forget to run ./bin/buildout after editing buildout.cfg

You can also customize the transcoding scripts inside the scripts directory.

