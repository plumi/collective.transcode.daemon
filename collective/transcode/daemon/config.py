listen_host='localhost'
listen_port='8888'
videofolder='videos'
secret='1771d99931264d538e75eeb19da7d6a0'

default_supported_mimetypes = ['application/ogg',
                                'video/ogg',
                                'video/x-ogg',
                                'video/x-ogm+ogg',
                                'video/flv',
                                'video/x-flv',
                                'video/mpeg',
                                'video/3gpp',
                                'video/x-ms-wmv',
                                'video/quicktime',
                                'video/x-la-asf',
                                'video/x-ms-asf',
                                'video/x-msvideo',
                                'video/mp4',
                                'video/webm',
                                ]

profiles = str([            
            {'id': 'jpeg',
             'cmd': './scripts/jpeg %s %s',
             'supported_mime_types': default_supported_mimetypes,
             'output_mime_type': 'image/jpeg',
             'output_extension': 'jpg' },
            {'id': 'mp4-high',
             'cmd': './scripts/mp4-high %s %s',
             'supported_mime_types': default_supported_mimetypes,
             'output_mime_type': 'video/mp4', 'output_extension': 'mp4' },
            {'id': 'mp4-low',
             'cmd': './scripts/mp4-low %s %s',
             'supported_mime_types': default_supported_mimetypes,
             'output_mime_type': 'video/mp4', 'output_extension': 'mp4' },
            {'id': './webm-high',
             'cmd': 'scripts/webm-high %s %s',
             'supported_mime_types': default_supported_mimetypes,
             'output_mime_type': 'video/webm', 'output_extension': 'webm' },
            {'id': './webm-low',
             'cmd': 'scripts/webm-low %s %s',
             'supported_mime_types': default_supported_mimetypes,
             'output_mime_type': 'video/webm', 'output_extension': 'webm' },
            ])
