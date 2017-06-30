"""
@author Gianfranco Micoli <micoli.gianfranco@gmail.com>

This module contains all usersettings related functions
"""

from django.conf import settings as djangosettings
from Core.models import Stats
import ConfigParser

import logging
logger = logging.getLogger(__name__)

def read():
    out = {}
    try:
        config = ConfigParser.ConfigParser()
        config.read(djangosettings.USERSETTINGS_PATH)
        options = config.options("TLS_Settings")
        for option in options:
            try:
                out[option] = config.get("TLS_Settings", option)
            except Exception as e:
                out[option] = None
    except Exception, e:
        logger.error("Error while reading settings: " + repr(e))
        logger.warning("Reloading default settings")
        out = {}
        for key, value in djangosettings.USERSETTINGS.iteritems():
            out[key] = value["default_value"]
        write(out)

        # TODO: Emit message "Default settings reloaded"
    return out

def write(new_settings):
    try:
        config = ConfigParser.ConfigParser()
        config.read(djangosettings.USERSETTINGS_PATH)
        if not config.has_section("TLS_Settings"):
            config.add_section("TLS_Settings")
        for stt in new_settings:
            config.set("TLS_Settings", stt, new_settings[stt])
        cfgfile = open(djangosettings.USERSETTINGS_PATH, 'w')
        config.write(cfgfile)
        cfgfile.close()
        for stat in Stats.objects():
            stat.delete()
        return True
    except Exception, e:
        logger.error("Error while writing settings: " + repr(e))
        return False