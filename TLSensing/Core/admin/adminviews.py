"""
@author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

from django.shortcuts import render
from django.http import HttpResponse
from Core.settings import settings
from Core.motes.sensor_constants import DEFAULT_THRESHOLDS

#############################################################

from Core.models import Mote
from Core.models import MoteBackup
from Core.models import Threshold
from Core.models import Stats
from Core.decorators import only_ajax
from Core.decorators import check_context
from Core.decorators import get_post_data
import xmlrpclib
import json
from urlparse import urlparse, parse_qs
import socket
from django.template.defaulttags import register
from django.conf import settings as djangosettings

import logging
logger = logging.getLogger("Core.views")

def clearStats():
    """
    Clears statistics cache
    """
    for stat in Stats.objects():
        stat.delete()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@only_ajax
@check_context
def main_subpage(request, *args, **kwargs):
    """
    Renders one of the subpages
    """
    try:
        if kwargs["page"] == "settings":
            # Load the settings
            sts = settings.read()
            # Load metadata for each setting and append to it
            # the current values read above
            data = djangosettings.USERSETTINGS
            for stt in sts:
                data[stt]["value"] = sts[stt]
            kwargs["context"]["data"] = data
            return render(request, 'ajax_admin_settings.html', kwargs["context"])

        if kwargs["page"] == "motes":
            kwargs["context"]["data"] = Mote.objects({}).only("alias_name", "ipv6", "measures", "mote_type")
            return render(request, 'ajax_admin_motes.html', kwargs["context"])

        if kwargs["page"] == "supervisor":
            try:
                server = xmlrpclib.Server('http://localhost:9001/RPC2')
                data = server.supervisor.getAllProcessInfo()
                supervisor_metadata = djangosettings.PROCESSES
                data_2 = []
                for i in xrange(0, len(data)):
                    data[i]["human_name"] = supervisor_metadata[data[i]["name"]]["human_name"]
                    data[i]["hide"] = supervisor_metadata[data[i]["name"]]["hide"]
                    # Remove TLSensing Web Server from the list.
                    # Leaving it there would be like putting an autodestruct button
                kwargs["context"]["data"] = data
                return render(request, 'ajax_admin_processes.html', kwargs["context"])
            except Exception, e:
                return render(request, "error_message.html", {"msg": "Can't connect to supervisor: " + repr(e)})
    except Exception, e:
        return HttpResponse(str(e))

@only_ajax
@check_context
@get_post_data
def settings_save(request, *args, **kwargs):
    try:
        sts_old = settings.read()
        sts_new = kwargs["post_data"]
        sts_djg = djangosettings.USERSETTINGS
        message = ""
        for stt in sts_old:    
            if sts_old[stt] != sts_new[stt]:
                message += sts_djg[stt]["delta_message"] + "\n"
        settings.write(sts_new)
        kwargs["context"]["result"]["status"] = "info"
        kwargs["context"]["result"]["message"] = message
        kwargs["page"] = "settings"
        return main_subpage(request, *args, **kwargs)
    except Exception, e:
        return HttpResponse(str(e))

@only_ajax
@check_context
@get_post_data
def supervisor_doaction(request, *args, **kwargs):
    server = xmlrpclib.Server('http://localhost:9001/RPC2')
    try:
        data = kwargs["post_data"]
        if kwargs["action"] == "start":
            server.supervisor.startProcess(data["process"])
            actionresultstring = "Process " + data["process"] + " started"
        if kwargs["action"] == "stop":
            server.supervisor.stopProcess(data["process"])
            actionresultstring = "Process " + data["process"] + " stopped"
        if kwargs["action"] == "restart":
            server.supervisor.stopProcess(data["process"])
            server.supervisor.startProcess(data["process"])
            actionresultstring = "Process " + data["process"] + " restarted"
        actionresult = "success"
    except Exception, e:
        actionresult = "error"
        actionresultstring = str(e)

    kwargs["context"]["result"] = {"status": actionresult, "message": actionresultstring}
    kwargs["page"] = "supervisor"
    return main_subpage(request, *args, **kwargs)

@only_ajax
@check_context
@get_post_data
def motes_doaction(request, *args, **kwargs):
    if kwargs["action"] == "remove":
        return motes_removeone(request, *args, **kwargs)
    if kwargs["action"] == "remove_data":
        return motes_removedata(request, *args, **kwargs)
    if kwargs["action"] == "add":
        return motes_addone(request, *args, **kwargs)
    return HttpResponse("WTF")

def motes_removedata(request, *args, **kwargs):
    actionresult = "error"
    actionresultstring = ""
    try:
        data = kwargs["post_data"]
        mts = Mote.objects(alias_name=data["alias_name"]).update(set__measures=[])
        actionresult = "success"
        actionresultstring = "Data removal complete"
        clearStats()
    except Exception, e:
        logger.error("Generic exception while removing mote data: " + str(e));
        actionresult = "error"
        actionresultstring = "Unable to delete data: " + repr(e)
    kwargs["context"]["result"] = {"status": actionresult, "message": actionresultstring}
    kwargs["page"] = "motes"
    return main_subpage(request, *args, **kwargs)

def motes_removeone(request, *args, **kwargs):
    actionresult = "error"
    actionresultstring = ""
    try:
        data = kwargs["post_data"]
        mts = Mote.objects(alias_name=data["alias_name"])
        if(len(mts) == 0):
            raise Exception("No motes found for Alias " + data["alias_name"])
        mote = mts[0]
        logger.info("Removing mote " + mote["ipv6"])
        if data["backup"] == True:
            motebackup = MoteBackup()
            motebackup["ipv6"] = mote["ipv6"]
            motebackup["alias_name"] = mote["alias_name"]
            motebackup["measures"] = mote["measures"]
            motebackup["mote_type"] = mote["mote_type"]
            motebackup["thresholds"] = mote["thresholds"]
            motebackup["notifications"] = mote["notifications"]
            motebackup.save()
        mote.delete()
        actionresult = "success"
        actionresultstring = "Mote \'" + data["alias_name"] + "\' successfully removed"
        if data["backup"] == True:
            actionresultstring += ". A backup has been saved"
        clearStats()
    except Exception as e:
        logger.error("Generic exception while removing mote: " + str(e));
        actionresult = "error"
        actionresultstring = str(e)
    kwargs["context"]["result"] = {"status": actionresult, "message": actionresultstring}
    kwargs["page"] = "motes"
    return main_subpage(request, *args, **kwargs)

def motes_addone(request, *args, **kwargs):
    actionresult = "error"
    actionresultstring = ""
    try:
        # If data["ipv6"] is not a valid IPv6 address string,
        # this call will raise socket.error.
        data = kwargs["post_data"]
        try:
            if data["ipv6"] == "":
                raise Exception("")    
        except Exception, e:
            raise Exception("Mote IPv6 address not specified")
        socket.inet_pton(socket.AF_INET6, data["ipv6"])
        try:
            if data["alias_name"] == "":
                raise Exception("")    
            data["alias_name"] = data["alias_name"].replace(' ','_')
        except Exception, e:
            raise Exception("Mote alias name not specified")

        mts = Mote.objects(alias_name=data["alias_name"])
        if(len(mts) > 0):
            raise Exception("Mote named " + data["alias_name"] + " already inserted in the testbed")
        mts = Mote.objects(ipv6=data["ipv6"])
        if(len(mts) > 0):
            raise Exception("Mote with ipv6 " + data["ipv6"] + " already inserted in the testbed")

        mote = Mote()
        mote.thresholds = Threshold()
        mote.thresholds.set(DEFAULT_THRESHOLDS[data["mote_type"]], data["mote_type"])
        mote.alias_name = data["alias_name"]
        mote.ipv6 = data["ipv6"]
        mote.mote_type = data["mote_type"]
        mote.save()
        actionresult = "success"
        actionresultstring = "Mote \'" + data["alias_name"] + "\' successfully added to the testbed"
        clearStats()
    except socket.error:
        actionresult = "error"
        actionresultstring = "Invalid IPv6 address"
    except Exception as e:
        logger.error("Generic exception while adding sensor: " + repr(e));
        actionresult = "error"
        actionresultstring = str(e)
    kwargs["context"]["result"] = {"status": actionresult, "message": actionresultstring}
    kwargs["page"] = "motes"
    return main_subpage(request, *args, **kwargs)