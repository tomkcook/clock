# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:35:40 2015

@author: tkcook
"""

import ringing as r
import web
import threading

g_ring_method = None

def start(ring_method):
    global g_ring_method
    urls = ('/ring/([^/]*)', 'web_ring')
    app = web.application(urls, globals())
    thread = threading.Thread(target=app.run)
    g_ring_method = ring_method
    thread.start()


class web_ring:
    def GET(self, name):
        if not name:
            name = 'stedman'
        g_ring_method(name)
        print 'Ringing method {0}'.format(name)
        return '''
        <html>
            <head>
                <title>Ringing</title>
            </head>
            <body>
                <h1>Enjoy some {0}!</h1>
            </body>
        </html>
        '''.format(name)
        
