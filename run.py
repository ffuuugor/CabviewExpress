import cherrypy
import logging

class EmptyApp(object):
    pass

if __name__ == '__main__':
    cherrypy.config.update('app.conf')
    cherrypy._cplogging.LogManager.access_log_format = '%(t)s "%(r)s" %(s)s "%(f)s"'
    cherrypy.quickstart(EmptyApp(), '/', 'app.conf')
