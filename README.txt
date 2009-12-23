Transcode Daemon (collective.transcode.daemon)
============

Introduction
============
collective.transcode.daemon is a fork of atreal's darksnow.convertdaemon (https://svn.atreal.net/public/svn.darksnow.org/ConvertDaemon) featuring improvements, and a code cleanout. 

How to get it working
============
Needs ffmpeg, python-twisted (on debian based systems install with #apt-get install ffmpeg, python-twisted, python-twisted-web2)


Configuration options
============
On buildout.cfg, upon transcodedaemon section, the following settings can be configured:

listen_host=locahost #ip or hostname to listen
listen_port=8888     #port to use
videofolder=videos   #path of folder where transcoded videos are stored

 
How can I change the quality and format of the transcoded files
============
You'll have to change the profiles list. On buildout.cfg, upon transcodedaemon section, edit the profiles ('low', 'high' are the defaults) to affect ffmpeg's behavior. 


Todo
============
Implement caching of downloads from the originating server. This will need to 
server to provide an md5sum (or other hash) of the original file so we won't
have to download it once for each profile (as is done now)
