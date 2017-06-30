"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
@contributor: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

# Django Base Command
from django.core.management.base import BaseCommand
from optparse import make_option
import ConfigParser
from optparse import OptionParser

# TLSensing Settings
from Core.settings import settings

# Models
from Core.models import Mote

# Motes functions
from Core.motes import motes
from Core.motes.charts import chart

# Redis
from Core.services import publish_message

import logging
import stat
import os
import sys
import time
import signal

logger = logging.getLogger(__name__)
avo_result = False
motes_replied = False

lockfilepath = "/var/tmp/acquire_lock"  # There's not one reason not to hardcode this variabile. It's not like it can be set by the admin
argsfilepath = "/var/tmp/acquire_args"  # There's not one reason not to hardcode this variabile. It's not like it can be set by the admin

def createLock(): 
    mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    with os.fdopen(os.open("/var/tmp/acquire_lock", os.O_WRONLY | os.O_CREAT, mode), 'w') as f:
        f.write(str(os.getpid()))
        logger.info("Lock file created")

def cleanExit():
    redismsg = {"status": "stopped"}
    if avo_result == True:
        if motes_replied == True:
            redismsg["pbar_class"] = "success"
            redismsg["pbar_msg"] = "Completed"
            redismsg["pbar_value"] = 100
        else:
            redismsg["pbar_class"] = "warning"
            redismsg["pbar_msg"] = "No motes have replied"
            redismsg["pbar_value"] = 100
    else:
        redismsg["pbar_class"] = "danger"
        redismsg["pbar_msg"] = "An error occurred"
    publish_message(redismsg, "avo_update")
    try:
        logger.info("Removing lock file")
        os.remove(lockfilepath)
    except Exception, e:
        logger.error(repr(e))

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    logger.warning("Received SIGTERM or SIGINT")
    cleanExit();
    logger.info("---------- VALUES ACQUISITION PROCESS EXITED ----------")
    sys.exit(0)

class Command(BaseCommand):
    help = """
        Acquire sensor values and plot <n_measures> points to chart;
        usage: python manage.py acquire_values <n_measures>"""


    option_list = BaseCommand.option_list + (
        make_option('--mote',
            action='store',
            dest='motes',
            default=False,
            help='Mote IPv6 separated by commas'),
        make_option('--meas',
            action='store',
            dest='measure_types',
            default=False,
            help='Measures to read'),
        )


    def handle(self, *args, **options):
        global avo_result
        global motes_replied
        avo_result = False
        motes_replied = False
        # Signals won't work if we're running the command using 
        # call_command
        try:
            killer = GracefulKiller()
        except Exception, e:
            logger.warning("Can't enable signal handling. Maybe the command has been started call_command?")
        """
        Handle the acquisition values workflow:
        1. Retrieve all not disabled motes;
        2. Acquire values from them;
        3. Compute some additional informations about measures, generate charts, publish message to client.
        """

        #Let's check if another process has a lock
        try:
            lockfile = open(lockfilepath, "r")
            logger.error("acquire_values cannot be started. Process " + lockfile.read() + " is currently reading!")
            sys.exit(0)
        except IOError as ex:
            logger.warning("Error reading lockfile: " + str(ex))
            createLock()

        #Check if arguments were specified using a file (workaround for supervisor not accepting arguments)
        try:
            config = ConfigParser.ConfigParser()
            config.read(argsfilepath)

            parser = OptionParser()
            parser.add_option('--meas',
                              action='store',
                              dest='measure_types',
                              help='Measures to read',
                              default=config.get("acquire_args", "measure_types"))
            parser.add_option('--mote',
                              action='store',
                              dest='motes',
                              help='Mote IPv6 separated by commas',
                              default=config.get("acquire_args", "motes"))

            for arg, argv in parser.parse_args()[0].__dict__.iteritems():
                options[arg] = argv
            logger.info("Using argument file")
            os.remove(argsfilepath)
        except Exception, e:
            logger.info("No argument file specified. Using command line arguments")

        logger.info("Arguments: " + str(options))

        try:
            publish_message({"status": "started"}, "avo_update")
            logger.info("---------- VALUES ACQUISITION PROCESS STARTED ----------")
            logger.info("Current Process PID: " + str(os.getpid()))
            n_measures = int(settings.read()["sampledmeasures"])
            
            if options["motes"]:
                motes_ipv6 = options["motes"].split(",")
                logger.info("Reading from specified motes: " + str(motes_ipv6))
            else:
                mts = Mote.objects().only("ipv6")
                logger.info("Reading from all " + str(len(mts)) + " motes")
                motes_ipv6 = list(mote.ipv6 for mote in mts)
            
            if options["measure_types"]:
                measure_types = options["measure_types"].split(",")
                logger.info("Reading specified measures: " + str(measure_types))
            else:
                measure_types = ["T", "H", "L", "A"]# TODO: to be changed according to new sensors names
                logger.info("Reading all measures")

            #read sensor values
            publish_message({"pbar_msg": "Acquiring data from enabled motes", "pbar_value": 0}, "avo_progress_update")
            logger.info("Acquiring data from enabled motes...")
            data = motes.get_readings(motes_ipv6, measure_types, n_measures)
            if len(data) > 0:
                motes_replied = True
                logger.info(("Data successfully acquired from motes with IPv6 ["+', '.join(['%s']*len(data.keys()))+"]") % tuple(data.keys()))
                #compute additional infos and send message to updates queue
                publish_message({"pbar_msg": "Computing additional data", "pbar_value": 100}, "avo_progress_update")
                logger.info("Computing additional data...")

                motes.compute_results(data.keys());
            else:
                logger.warning("No motes have replied! Avoiding computation")
            
            logger.info("---------- VALUES ACQUISITION PROCESS ENDED ----------")
            avo_result = True
        except Exception as e:
            logger.error("Generic Exception while acquiring sensor values from motes: %s" %repr(e))
        finally:
        	cleanExit()
