import cherrypy
import logging

class EmptyApp(object):
    pass

if __name__ == '__main__':
    cherrypy.config.update('app.conf')
    cherrypy.quickstart(EmptyApp(), '/', 'app.conf')
