"""
@author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

import xmlrpclib
from django.conf import settings as djangosettings
import logging
logger = logging.getLogger(__name__)

def getProcessInfo(process):
    try:
        server = xmlrpclib.Server(djangosettings.SUPERVISOR_URL)
        return server.supervisor.getProcessInfo(process)
    except Exception, e:
        return {}
        logger.info(__name__)

def startProcess(process):
    try:
        server = xmlrpclib.Server(djangosettings.SUPERVISOR_URL)
        return server.supervisor.startProcess(process)
    except Exception, e:
        logger.info(__name__)