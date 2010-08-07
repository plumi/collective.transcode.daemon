listen_host='localhost'
listen_port='8888'
videofolder='videos'
secret='1771d99931264d538e75eeb19da7d6a0'

default_supported_mimetypes = [ 'video/mpeg', 
                                'video/3gpp', 
                                'video/x-ms-wmv', 
                                'video/ogg', 
                                'video/x-ogg', 
                                'video/x-ogm+ogg', 
                                'video/quicktime', 
                                'video/x-la-asf', 
                                'video/x-ms-asf', 
                                'video/x-msvideo',
                                'video/mp4',
                              ]

profiles = [
        {'id' : 'low', 
         'cmd' : 'ffmpeg -y -i %s -s 424x344 -qscale 5.0 -r 30 -ar 44100 -f flv %s', 
         'supported_mime_types': default_supported_mimetypes,
        }, 
        {'id' : 'high', 
         'cmd' : 'ffmpeg -y -i %s -s 640x480 -qscale 5.0 -r 50 -ar 44100 -f flv %s', 
         'supported_mime_types': default_supported_mimetypes,
        }
       ]
