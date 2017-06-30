"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

# Django Rendering
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
import ConfigParser

# Django Management
from django.core.management import call_command

# Django Settings
from django.conf import settings as djangosettings
from Core.settings import settings

# Decorators
#from Core.decorators import mote_object
from Core.decorators import only_ajax
from Core.decorators import check_context
from Core.decorators import methods
from Core.decorators import defaults

# Motes functions
from Core.motes import motes

# Supervisor
from Core.admin import supervisor

# Login
from passlib.hash import pbkdf2_sha256
#from django.views.decorators.csrf import csrf_exempt,csrf_protect


from coap import coap
from coap import coapException
from Core.motes import sensor_constants

import os
import logging
logger = logging.getLogger(__name__)

def render_error(msg):
    """
    Renders a default error string
    """
    return render_to_string('error_message.html', {"msg": msg})

@defaults
@methods(["GET"])
def render_section(request, *args, **kwargs):
    if kwargs["section_name"] == "main-stats":
        return section_main_stats(request, *args, **kwargs)
    if kwargs["section_name"] == "mote-panel":
        return section_mote_panel(request, *args, **kwargs)
    return HttpResponse("Can't render " + kwargs["section_name"])

@defaults
@methods(["GET"])
def index(request, *args, **kwargs):
    """
    Renders the index view
    """
    # Uncomment to debug
    #return section_mote_panel(request, argument="43eb45c4f926b339f1e4bcd3", out={})
    #return section_main_stats(request, out={})

    # Get motes informations
    kwargs["out"]["motes"] = sorted([mote.as_dict() for mote in motes.get()], key=lambda k: k['alias_name'])
    kwargs["out"]["motecount"] = motes.count()

    # Get redis status, to display an alert if the process is not running
    processinfo = supervisor.getProcessInfo("redis-server")
    if processinfo != {}:
        if processinfo["statename"] != "RUNNING":
            kwargs["out"]["processinfo"] = {"post": False, "bold": "Redis is not started!", "msg": "TLSensing needs it to work properly. Please contact an administrator"}
        else:
            kwargs["out"]["processinfo"] = {"post": True}
    else:
        kwargs["out"]["processinfo"] = {"post": False, "bold": "Couldn't connect to supervisor!", "msg": "TLSensing needs it to work properly. Please contact an administrator"}

    # Accordions shown for each mote section
    kwargs["out"]["accordions"] = djangosettings.ACCORDIONS
    kwargs["out"]["measure_types"] = djangosettings.MEASURE_TYPES
    kwargs["out"]["coap_queries"] = djangosettings.COAP_QUERIES
    return render(request, "index.html", kwargs["out"])

@defaults
@methods(["GET"])
def run_avo(request, *args, **kwargs):
    supervisor.startProcess("acquire-values-oneshot")
    return HttpResponse("")


@defaults
@methods(["GET"])
def log_in(request, *args, **kwargs):
    #credentials_file=open("/home/tlsensing/credentials.txt",'w')
    credentials_file=open("/home/tlsensing/TLSEnv/TLSensing/Core/admin/credentials.txt",'rb')
    expected_hash=credentials_file.read().decode('utf-8')
    credentials_file.close()
    if pbkdf2_sha256.verify(kwargs["pwd"],expected_hash) == True:
	#success
	msg='Admin authenticated'
	return HttpResponse('Admin authenticated',status=200) #Http success ok
    else:
	#failure   
	msg='Authentication failed. Please check the password'
	return HttpResponse('Authentication failed. Please check the password',status=401) #Http client error unauthorized

@defaults
@methods(["GET"])
def check_password(request, *args, **kwargs):
    #credentials_file=open("/home/tlsensing/credentials.txt",'w')
    credentials_file=open("/home/tlsensing/TLSEnv/TLSensing/Core/admin/credentials.txt",'rb')
    expected_hash=credentials_file.read().decode('utf-8')
    credentials_file.close()
    if pbkdf2_sha256.verify(kwargs["opwd"],expected_hash) == True:
	#success
	msg='Admin authenticated'
	return HttpResponse('Admin authenticated',status=200) #Http success ok
    else:
	#failure   
	msg='Authentication failed. Please check the password'
	return HttpResponse('Authentication failed. Please check the password',status=401) #Http client error unauthorized
    
@defaults
@methods(["GET"])
def store_newpwd(request, *args, **kwargs):
    hash_result = pbkdf2_sha256.using(rounds=10000, salt_size=10).hash(kwargs["npwd"])
    encoded_hash = hash_result.encode('utf-8')
    credentials_file=open("/home/tlsensing/TLSEnv/TLSensing/Core/admin/credentials.txt",'wb')
    credentials_file.truncate()
    credentials_file.write(encoded_hash)
    credentials_file.close()   
    msg='Password successfully changed.'
    return HttpResponse(msg,status=200) #Http success
    

@defaults
@methods(["POST"])
def poll(request, *args, **kwargs):
    ipv6_list = [motes.get(mote_id=kwargs["mote_id"]).first().ipv6]
    measure_types = kwargs["post_data"]["sensor"]
    #call_command('acquire_values_oneshot', motes=",".join(ipv6_list), measure_types=",".join(measure_types))
    cfgfile = open("/var/tmp/acquire_args", 'w')
    Config = ConfigParser.ConfigParser()
    Config.add_section('acquire_args')
    Config.set('acquire_args','motes', ",".join(ipv6_list))
    Config.set('acquire_args','measure_types', ",".join(measure_types))
    Config.write(cfgfile)
    cfgfile.close()
    supervisor.startProcess("acquire-values-oneshot")
    #get_readings(ipv6_list, measure_types)
    return HttpResponse("OK")

@defaults
@methods(["GET", "POST"])
def thresholds(request, *args, **kwargs):
    """
    Update thresholds for the given mote.
    """
    if request.method == "GET":
        kwargs["out"]["mote"] = motes.get(mote_id=kwargs["mote_id"])[0].as_dict()
        kwargs["out"]["measure_types"] = djangosettings.MEASURE_TYPES
        return render(request, "index_modals_motes_thresholds.html", kwargs["out"])
    else:        
        mote = motes.get(mote_id=kwargs["mote_id"])[0]
        thresholds = {}
        if "__reset" in kwargs["post_data"]:
            mote.thresholds.set(sensor_constants.DEFAULT_THRESHOLDS[mote.mote_type], mote.mote_type)
            thresholds = sensor_constants.DEFAULT_THRESHOLDS[mote.mote_type]
            thresholds["_msg"] = "Thresholds resetted"
        else:
            for data in kwargs["post_data"]:
                th_measure = data["key"][4:-4]   # Remove {max,min}- and -{msg,val}
                thresholds[th_measure] = {}
                thresholds[th_measure]["max"] = {}
                thresholds[th_measure]["min"] = {}

            for data in kwargs["post_data"]:
                th_measure = data["key"][4:-4]   # Remove {max,min}- and -{msg,val}
                th_maxmin = data["key"][:3]      # max or min
                th_msgval = data["key"][-3:]     # msg or val
                thresholds[th_measure][th_maxmin][th_msgval] = float(data["val"]) if th_msgval == "val" else data["val"]

            mote.thresholds.set(thresholds, mote.mote_type)
            thresholds = {} # We don't need to send back all the data
            thresholds["_msg"] = "Thresholds saved"
        
        mote.save()
        import json
        return HttpResponse(json.dumps(thresholds, ensure_ascii=True))

######################################################################
# MAIN STATS
######################################################################
def section_main_stats(request, *args, **kwargs):
    # Get motes data
    mts = motes.get()

    # Get motes informations
    kwargs["out"]["motes"] = [mote.as_dict() for mote in mts]

    # Get motes count and merge with mote properties
    # mote_type: {'count': 6, 'label': 'OpenMote'}
    kwargs["out"]["motecount"] = motes.count()
    kwargs["out"]["main_stats"] = main_stats()
    return render(request, "index_section_main-stats.html", kwargs["out"])

def main_stats():
    #td = motes.stats(mts)
    td = motes.stats("all")
    if td != {}:
        if td["data"]["data"] != []:
            return render_to_string('mote_stats_all.html', td["data"])
        else:
            return render_error("No measures found");
    else:
        return render_error("No measures found");

######################################################################
# MOTE PANEL
######################################################################
def render_accordion(name, label, content):
    return render_to_string("accordion.html", {"name": name, "label": label, "content": content})

def section_mote_panel(request, *args, **kwargs):
    # Variable for easier code readability
    mote_id = kwargs["argument"]
    
    # Get the mote
    mote = motes.get(mote_id=mote_id)[0]

    # Format the mote as dict
    kwargs["out"]["mote"] = mote.as_dict()

    # Get possible "Poll now" queries
    kwargs["out"]["coap_queries"] = djangosettings.COAP_QUERIES

    # Get mote history for left side
    kwargs["out"]["mrv"] = mote_history(mote, "list", 1)

    # Get accordions
    accs = []
    for accordion in djangosettings.ACCORDIONS:
        if mote.mote_type in accordion["mote_types"]:
            if accordion["callback"] != "":
                content = eval(accordion["callback"])
            else:
                content = "TBD"
            accs.append(render_accordion(accordion["name"] + "-" + mote_id, accordion["label"], content))
    kwargs["out"]["accordions"] = accs
    
    return render(request, "index_section_mote-panel.html", kwargs["out"])

######################################################################
# ACCORDIONS
######################################################################
def notifications(mote, n_notifications):
    data = {}
    if len(mote.notifications) > 0:
        #Get notifications
        data["notifications"] = [notification.as_dict() for notification in mote.notifications]

        # Render the template
        return render_to_string("notifications.html", data)
    else:
        return render_error("No notifications found")

def mote_history(mote, h_format, n_measures=int(settings.read()["sampledmeasures"])):
    measures = mote.get_measures(n_measures=n_measures)
    # Get mote data
    data = {}
    if len(measures) > 0:
        # Get measure types metadata. They will be needed to determine 
        # if a measure has to be shown depending on the mote typology
        data["measure_types"] = [mt for mt in djangosettings.MEASURE_TYPES if mote.mote_type in mt["mote_types"]]

        # Get measures array
        data["measures"] = measures
        #return HttpResponse(str(kwargs["out"]["measures"]))

        # Render the template
        return render_to_string("mote_history_" + h_format + ".html", data)
    else:
        return render_error("No measures found")

def mote_stats(mote):
    td = motes.stats(str(mote.id))
    if td["data"] != []:
        if td["data"]["data"] != []:
            return render_to_string('mote_stats.html', td["data"])
    else:
        return render_error("No measures found");

def graphs(mote, chart_type):
    if mote.chart_exists(chart_type):
        return render_to_string('mote_charts.html', {"chart": mote.get_chart(chart_type).read()})
    else:
        return render_to_string('error_message.html', {"msg": "Graph not found"})
    #req_file = os.path.join(CHART_URL, "mote_%s-%s.svg" %(chart_type, mote.id))
    # if os.path.isfile(req_file):
    #     with  as chart:
    #         return render_to_string('mote_charts.html', {"chart": chart.read()})

def chart(request, *args, **kwargs):
    """
    Return a generated chart, given a mote and chart type

    @param request: the incoming request
    @param mote_id: the mote id
    @param type_mote: the type of mote
    @return the requested chart, if it exists
    """
    #try:
    req_file = os.path.join(CHART_URL, "mote_%s-%s.svg" %(kwargs["chart_type"], kwargs["mote_id"]))
    if os.path.isfile(req_file):
        with open(os.path.join(CHART_URL, "mote_%s-%s.svg" %(kwargs["chart_type"], kwargs["mote_id"])), "rb") as chart:
            #return HttpResponse(str(chart))
            return render(request, 'mote_charts.html', {"chart": chart.read()})
    else:
        return render(request, 'error_message.html', {"msg": "Graph not found"})
############################################################################

#TODO: Non eliminare ancora, devo vedere ancora per il pannello di controllo
# def add_remove_mote(request, *args, **kwargs):
#     """
#     Add or remove mote views.
#     When adding, check if the provided IPv6 params is already associated to
#     a registered mote.
#     Check if the HTTP request is well formed, analyzing the passed data;
#     return specific error if a validation condition is not met.

#     @param request: the incoming request
#     @return the index view as HTML
#     """
# #    return
#     if "type" in request.POST and request.POST["type"] == "remove":
#         motes = remove_sensor(kwargs["mote"], request.POST)
            
#     elif "type" in request.POST and request.POST["type"] == "add":
#         try:
#             if Mote.objects.filter(ipv6=request.POST["ipv6"]).count() == 1:
#                 logger.error("Address already in use: %s" %request.POST["ipv6"])
#                 return HttpResponse("Address already in use", status=BAD_REQUEST)
#             motes = add_sensor(request.POST)
#         except socket.error:
#             logger.error("Invalid IPv6: %s" %request.POST["ipv6"])
#             return HttpResponse("Invalid IPv6", status=BAD_REQUEST)
#     if not motes is None:
#         return render(request, "motes.html", dict(motes=motes)) 
#     logger.error("Unexpected error! Data: %s" % (" ".join(["%s:%s" %(key, request.POST[key]) for key in request.POST.keys()])))
#     return HttpResponse("Something is wrong", status=INTERNAL_SERVER_ERROR)

def dashboard(request, action="", *args, **kwargs):
    return render(request, 'dashboard.html')

def doaction(request, *args, **kwargs):
    return HttpResponse("OK")

#TODO: Da testare
#@mote_object
def discovery(request, *arg, **kwargs):
    """
    Verify that mote_id is ready to transmit sensor readings.

    @param request: the incoming request
    """
    response = render(request, "index_motecontent_availabilityalert.html", {'alerttype': 'success', 'message': 'Mote available'});

    try:
        mts = motes.get(mote_id=kwargs["mote_id"])
        resources = motes.coap_wellknown(mts[0].ipv6)
    except coapException.coapTimeout:
        response = render(request, "index_motecontent_availabilityalert.html", {'alerttype': 'danger', 'message': 'Request timeout'});
    except coapException.coapException:
        response = render(request, "index_motecontent_availabilityalert.html", {'alerttype': 'danger', 'message': 'Unable to probe the mote!'});
    else:
         sensordata_L= '/L'
#
#        Before the last update, this function used to check if SENSORDATA_RES (defined in Core/motes/sensor_constants.py as /sens) was in #	  resources, but with the new firmware there is no more /sens resource but four resources named /A, /L, /H, /T. For this reason, now #         mote availability is checked using one of these resources - specifically the Light one.    
#
#         
	 #if sensor_constants.SENSORDATA_RES not in resources:
	 if sensordata_L not in resources:
            logger.error("Required CoAP resource '{0}' is not installed on mote at {1}".format(
                sensor_constants.SENSORDATA_RES, mts[0].ipv6))
            response = render(request, "index_motecontent_availabilityalert.html", {'alerttype': 'danger', 'message': 'CoAP resource {0} unavailable'.format(sensor_constants.SENSORDATA_RES) });

    return response
