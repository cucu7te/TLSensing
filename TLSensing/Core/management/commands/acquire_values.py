"""
@author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

from django.core.management.base import BaseCommand

# Redis
from Core.services import publish_message

from Core.settings import settings
from Core.admin import supervisor

import signal
import sched, time
import xmlrpclib
import os
import time
import errno
import sys
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)
s = sched.scheduler(time.time, time.sleep)

class TimeoutExpired(Exception):
    pass

def pid_exists(pid):
    """Check whether pid exists in the current process table."""
    if pid < 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError, e:
        return e.errno == errno.EPERM
    else:
        return True

def wait_pid(pid, timeout=None):
    def check_timeout(delay):
        if timeout is not None:
            if time.time() >= stop_at:
                raise TimeoutExpired
        time.sleep(delay)
        return min(delay * 2, 0.04)
    if timeout is not None:
        waitcall = lambda: os.waitpid(pid, os.WNOHANG)
        stop_at = time.time() + timeout
    else:
        waitcall = lambda: os.waitpid(pid, 0)
    delay = 0.0001
    while 1:
        try:
            retpid, status = waitcall()
        except OSError, err:
            if err.errno == errno.EINTR:
                delay = check_timeout(delay)
                continue
            elif err.errno == errno.ECHILD:
                # This has two meanings:
                # - pid is not a child of os.getpid() in which case
                #   we keep polling until it's gone
                # - pid never existed in the first place
                # In both cases we'll eventually return None as we
                # can't determine its exit status code.
                while 1:
                    if pid_exists(pid):
                        delay = check_timeout(delay)
                    else:
                        return
            else:
                raise
        else:
            if retpid == 0:
                # WNOHANG was used, pid is still running
                delay = check_timeout(delay)
                continue
            # process exited due to a signal; return the integer of
            # that signal
            if os.WIFSIGNALED(status):
                return os.WTERMSIG(status)
            # process exited using exit(2) system call; return the
            # integer exit(2) system call has been called with
            elif os.WIFEXITED(status):
                return os.WEXITSTATUS(status)
            else:
                # should never happen
                raise RuntimeError("unknown process exit status")

def do_something(sc):
    logger.info("Starting data acquisition process")
    try:
        supervisor.startProcess("acquire-values-oneshot")
        # Sleep 3 seconds to let the supervisor realize if the process started correctly
        time.sleep(3)
        message = "acquire_values_oneshot didn't start properly! Bailing out..."
    except Exception, e:
        #If we can't start it, it may already be started
        message = "Error while starting the acquisition process: " + repr(e)
    avo_info = supervisor.getProcessInfo("acquire-values-oneshot")
    if avo_info["statename"] == "RUNNING":
        #print "Process detected as running. Waiting for it to finish"
        pid = int(avo_info["pid"])
        wait_pid(pid)
        interval = int(settings.read()["pullacquisition_interval"])
        publish_message({"next_acquisition": '{:%d/%b/%Y %H:%M:%S}'.format(datetime.now() + timedelta(minutes=interval))}, "avs_update")
        logger.info("Next acquisition in " + str(interval) + " minutes, at " + '{:%H:%M:%S}'.format(datetime.now() + timedelta(minutes=interval)))
        sc.enter(interval*60, 1, do_something, (sc,))
    else:
        logger.info(message)
        sys.exit(1)

def cleanExit():
    publish_message({'avs': 'stopped'}, "avs_update")

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    logger.info("Received SIGTERM or SIGINT")
    cleanExit();
    logger.info(" ---------- VALUES ACQUISITION SCHEDULER EXITED ----------")
    sys.exit(0)

class Command(BaseCommand):
    def handle(self, *args, **options):
        killer = GracefulKiller()
        logger.info(" ---------- VALUES ACQUISITION SCHEDULER STARTED ----------")
        first_start_timeout = 5
        logger.info("Acquisition will commence in " + str(first_start_timeout) + " seconds")
        s.enter(first_start_timeout, 1, do_something, (s,))
        s.run()