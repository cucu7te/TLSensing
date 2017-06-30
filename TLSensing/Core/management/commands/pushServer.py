"""
@author: Giacomo Donato Cascarano <gd.cascarano@gmail.com>
    
This module defines a django command to start a CoAP push server. The server listens on the specified port and resource path.
    
@date: July 15
"""

from django.core.management.base import BaseCommand
from coap import coap
from coap import coapException
import Core.pushserver.serverResource as serverResource
from Core.settings import settings

import signal, os

class Command(BaseCommand):
    help = """Start Push Server
	      usage: python manage.py pushServer [port resourceName]
	      default: python manage.py pushServer 5683 sens"""

    def handle(self, *args, **options):
        if len(args) == 0:
            port = int(settings.read()["pushserver_coapport"])
            res = '/sens'
        elif len(args) == 2:
            try:
                port = int(args[0])
                res = '/{0}'.format(args[1])
            except ValueError:
                print self.help
                return
        else:
            print self.help
            return

        print 'Starting push server...'
        coap_obj = coap.coap(ipAddress='', udpPort=port);
        resource = serverResource.serverResource(res)
        coap_obj.addResource(resource);

        signal.signal(signal.SIGINT, handler)
        print 'Port: {0}\nResource: {1}'.format(port, res)
        print 'Quit the server with CONTROL-C\n'
        #raw_input(' ')
        signal.pause()

        # close
        coap_obj.close()

def handler(signum, frame):
    print '...'
