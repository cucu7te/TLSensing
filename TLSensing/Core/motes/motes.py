"""
@author Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

# Settings
from django.conf import settings as djangosettings
from Core.settings import settings

# Models
from Core.models import Mote
from Core.models import Measure
from Core.models import Notification
from Core.models import Stats

# CoAP Python Library
from coap import coap
from coap import coapException

# Redis
from Core.services import publish_message

import numpy
import random
import time
import struct
import socket

import logging
logger = logging.getLogger(__name__)

# Da rimuovere
from Core.motes import sensor_constants
from Core.motes.charts import chart

class SensorData(object):
    def __getitem__(self, key):
        return getattr(self, key)

    def randomize(self):
        self.accel_x = random.random() * 10
        self.accel_y = random.random() * 10
        self.accel_z = random.random() * 10
        self.light = random.random() * 10
        self.temperature = random.random() * 10
        self.humidity = random.random() * 10

def get(mote_ipv6="", mote_id="", mote_alias=""):
    """
    Returns all motes, with all the measures
    """
    # Retrieve motes
    if mote_ipv6 != "":
        motes = Mote.objects(ipv6=mote_ipv6)
    elif mote_id != "":
        motes = Mote.objects(id=mote_id)
    elif mote_alias != "":
        motes = Mote.objects(alias_name=mote_alias)
    else:
        motes = Mote.objects()
    return motes

#{"statid": statid, "data": sorted(table_data["data"], key=lambda k: k["measure_type"], reverse=True)}
def stats(statid, count=0):
    if len(Stats.objects(statid=statid)) > 0:
        logger.info("[STATS] Cache hit for stat " + statid)
        return Stats.objects(statid=statid)[0].as_dict()
    else:
        logger.info("[STATS] Recalculating and reloading stat " + statid)
        if statid != "all":
            calculate_stats(get(mote_id=statid))
        else:
            calculate_stats(get())
        if count > 0:
            return {}
        else:
            return stats(statid, 1)

def calculate_stats(mts):
    n_measures = int(settings.read()["sampledmeasures"])
    stats = {"n_measures": n_measures, "data": []}

    #TODO: This won't scale for measures done for just two motes.
    if len(mts) > 1:
        statid = "all"
    else:
        statid = str(mts[0].id)
    #logger.info("Calculating stats for " + statid + ", " + str(n_measures) + " measures")

    for mote in mts:
        for mt in djangosettings.MEASURE_TYPES:
            measures = mote.get_measures(mt["field"], n_measures)
            if len(measures) > 0:
                # Get statistics
                stats["data"].append({
                    "mote": mote["alias_name"],
                    "measure_type": mt["field"],
                    "max": max(measures, key=lambda x:x['value']),
                    "min": min(measures, key=lambda x:x['value']),
                    "avg": round(numpy.mean([meas["value"] 
                        for meas in measures]), 2)
                })

    table_data = {"n_measures": stats["n_measures"], "data": []}
    if stats["data"] != []:
        sd = stats["data"]
        dmt = djangosettings.MEASURE_TYPES
        for t in dmt:
            indexes = [stat["measure_type"] == t["field"] for stat in sd]
            dic = {"measure_type": t["label"]}  # TODO: Maybe put the identifier here and get the label in the view. To simplify we'll get the label here
            if True in indexes:
                maxstat = max([stat for stat in sd if stat["measure_type"] == t["field"]], key=lambda x: x["max"]["value"])
                minstat = min([stat for stat in sd if stat["measure_type"] == t["field"]], key=lambda x: x["min"]["value"])
                dic["max"] = dict(maxstat["max"],**{"mote": maxstat["mote"]})
                dic["min"] = dict(minstat["min"],**{"mote": minstat["mote"]})
                dic["avg"] = round(numpy.mean([stat["avg"] for stat in sd if stat["measure_type"] == t["field"]]), 2)
            # If there's no data we only append the table
            table_data["data"].append(dic)

    db_stats = Stats.objects(statid=statid)
    if len(db_stats) > 0:
        s = db_stats[0]
    else:
        s = Stats()
    s.statid = statid
    s.data = {"n_measures": n_measures, "data": sorted(table_data["data"], key=lambda k: k["measure_type"], reverse=True)}
    s.save()
    #return {"statid": statid, "data": sorted(table_data["data"], key=lambda k: k["measure_type"], reverse=True)}

def count():
    """
    Returns a dictionary with motes count for each mote type.
    Used in the main table
    """
    mote_types = djangosettings.MOTE_TYPES
    data = {}
    counts = Mote.objects.exec_js("""db.mote.aggregate([{"$group" : {_id: "$mote_type", count: {$sum:1}}}])""")
    # _firstBatch for MongoDB 2.6
    #for mote in counts["_firstBatch"]:
    for mote in counts["result"]:
        data[mote["_id"]] = {}
        data[mote["_id"]]["count"] = int(mote["count"])

    for mt in data:
        #mote_types[mt]["count"] = 0
        for k in data[mt]:
            mote_types[mt][k] = data[mt][k]
    return mote_types

def check_thresholds(mts):
    """
    Compares last measure with thresholds to send a notification
    if values exceed or are lower than the max/min threshold
    """
    for mote in mts:
        # Get last measure
        measure = mote.get_measures(n_measures=1)[0]
        # Get mote thresholds
        thresholds = mote.thresholds.as_dict()
        # Get mote alias to display in the notification
        mote_name = mote.alias_name
        for th, thdict in thresholds.iteritems():
            if measure[th] != None:
                print "Type: " + str(th) + " | Measure: " + str(measure[th]) + " | Max th: " + str(thdict["max"]) + " | Min th: " + str(thdict["min"])
                if measure[th] > float(thdict["max"]["val"]):
                    publish_message({"mote": mote_name, "msg": thdict["max"]["msg"]}, "notifications")
                    n = Notification()
                    n.message = thdict["max"]["msg"]
                    n.not_type = "Max"
                    n.measure = th
                    mote.notifications.append(n)
                    mote = mote.save()
                    print thdict["max"]["msg"]

                if measure[th] < float(thdict["min"]["val"]):
                    publish_message({"mote": mote_name, "msg": thdict["min"]["msg"]}, "notifications")
                    n = Notification()
                    n.message = thdict["min"]["msg"]
                    n.not_type = "Min"
                    n.measure = th
                    mote.notifications.append(n)
                    mote = mote.save()
                    print thdict["min"]["msg"]

def compute_results(motes_ipv6):
    """
    Control the post-aquisition process and send updated data to messages queue.

    @param n_measures: points to be plotted out
    """

    # Generating charts
    logger.info("Generating charts")
    chart(motes_ipv6, int(settings.read()["sampledmeasures"]))

    # Checking for thresholds
    logger.info("Checking thresholds and calculating statistics")
    for ip in motes_ipv6:
    	mote = get(mote_ipv6=ip)
        calculate_stats(mote)
        check_thresholds(mote.fields(slice__measures=-1))
    logger.info("Calculating global statistics")
    calculate_stats(get())

def coap_wellknown(ip, ackTimeout=sensor_constants.DEFAULT_ACK_TIMEOUT, respTimeout=sensor_constants.DEFAULT_RESP_TIMEOUT):
    """
    Obtain a string listing the known CoAP resources installed on an endpoint.

    @param ip: the IPv6 address of the CoAP endpoint.
    @return a comma-separated sequence of resource paths formatted
    as the string '</path1>,</path2>,...'

    @raise coapException.coapTimeout: if the GET request times out.
    @raise coapException.coapException: if another reason prevents the
    GET request from being fulfilled.
    """ 
    # Initialize and configure the CoAP socket with a random port
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    port = int(sock.getsockname()[1])
    sock.close()
    coap_obj = coap.coap(udpPort=port)
    coap_obj.ackTimeout = 2*ackTimeout
    coap_obj.respTimeout = 2*respTimeout

    resources = ''

    try:
        # Query the resource
        payload = coap_obj.GET(uri='coap://[{0}]/.well-known/core'.format(ip))
    except coapException.coapTimeout as ex:
        logger.warning("Request to mote at %s timed out." %ip)
        raise ex
    except coapException.coapException as ex:
        logger.error("Generic error while querying mote at: %s" %ip)
        raise ex
    else:
        resources = ''.join([chr(b) for b in payload])
    finally:
        # Close the socket
        coap_obj.close()

    return resources

def get_readings(motes, sensor_values, redis=False):
    readings = {}
    publish_message({"errors": ""}, "avo_progress_error_update")

    # Format the CoAP query string
    query = ''
    if len(sensor_values) > 0:
        query = '&'.join(sensor_values)

    if redis:
        step_progress = 80/len(motes)
        tot_step = 0

    errorshtml = ""
    for ip in motes:
        try:
            if redis:
                tot_step = tot_step + step_progress/2
                publish_message({"pbar_msg": "Reading from mote with IPv6: %s.." % ip, "pbar_value": tot_step}, "avo_progress_update")

            # Read from motes
            logger.info("Reading from mote %s.." % ip)
            # if djangosettings.DEBUG:
            #     logger.info("Debugging enabled. Using random values!")
            #     sd = SensorData()
            #     sd.randomize()
            #     reading = {ip: sd.__dict__}
            #     time.sleep(3)
            # else:
            reading, error = sensor_query(ip, query, redis)
            if redis:
                if error != "":
                    errorshtml += error
                    publish_message({"errors": errorshtml}, "avo_progress_error_update")

            if reading == None:
                logger.info("Empty reading!")
            else:
                if redis:
                    tot_step = tot_step + step_progress/2
                    publish_message({"pbar_msg": "Storing data for mote %s.." % ip, "pbar_value": tot_step}, "avo_progress_update")
                logger.info("Storing data for mote with IPv6: %s" % ip)
                r = {}
                for sv in sensor_values:
                    for v in djangosettings.COAP_QUERIES[sv]["measure_types"]:
                        r[v] = round(reading[ip][v], 2)
                logger.info("Data: " + str(r))

                mote = Mote.objects(ipv6=ip)[0]
                mote.measures.append(Measure(**(r)))
                mote.save()

                # All right! We can save on the data structure in RAM
                readings[ip] = r
        except Exception, e:
            logger.error(repr(e))
    return readings

def sensor_query(mote_ipv6, query, redis=False):
    status = False
    error = ""
    # Initialize and configure the CoAP socket
    try:
        coapport = int(settings.read()["pullacquisition_coapport"])
        logger.info("Inizializing CoAP socket at port " + str(coapport))
        coap_obj = coap.coap(udpPort=coapport)
        coap_obj.ackTimeout = sensor_constants.DEFAULT_ACK_TIMEOUT
        coap_obj.respTimeout = sensor_constants.DEFAULT_RESP_TIMEOUT

        # Fix argument formatting
        resource = sensor_constants.SENSORDATA_RES
        if resource[0] != '/':
            resource = '/' + resource
        if query != '' and query[0] != '/':
            query = '/' + query

#####        if query != '' and query[0] != '?':
#####            query = '?' + query
           
        sensor_list = []
        
        if "&" in query:
            sensor_list = query.split("&")
        else:
            sensor_list.append(query)
        #logger.info(sensor_list)

        # Build the full URI for the request
#####        request_uri = 'coap://[{0}]{1}{2}'.format(mote_ipv6, resource, query)

        # Get a new SensorData instance
        sensordata = SensorData()
        
        for res in sensor_list:
            if res != "" and res[0] != "/":
                res = "/" + res
            res = res[0:2].upper()
            request_uri = 'coap://[{0}]{1}'.format(mote_ipv6, res)
            logger.info("Querying " + request_uri)
            payload = coap_obj.GET(request_uri)
            logger.info("Reading completed successfully")
            logger.info("Unpacking and processing data")
            if sensor_constants.HUMIDITY_QUERY in res:
                (sensordata.humidity, ) = struct.unpack_from('<f',
                    bytearray(payload[sensor_constants.HUMIDITY_LOWER:sensor_constants.HUMIDITY_UPPER]))
                logger.info("*** humidity: " + str(sensordata.humidity))
            elif sensor_constants.TEMPERATURE_QUERY in res:
                (sensordata.temperature, ) = struct.unpack_from('<f',
                    bytearray(payload[sensor_constants.TEMPERATURE_LOWER:sensor_constants.TEMPERATURE_UPPER]))
                logger.info("*** temperature: " + str(sensordata.temperature))
            elif sensor_constants.LIGHT_QUERY in res:
                (sensordata.light,) = struct.unpack_from('<f',
                    bytearray(payload[sensor_constants.LIGHT_LOWER:sensor_constants.LIGHT_UPPER]))
                logger.info("*** light: " + str(sensordata.light))
            elif sensor_constants.ACCEL_QUERY in res:
                (sensordata.accel_x, sensordata.accel_y, sensordata.accel_z) = struct.unpack_from('<hhh',
                    bytearray(payload[sensor_constants.ACCEL_LOWER:sensor_constants.ACCEL_Z_UPPER]))
                logger.info("*** accel_x: " + str(sensordata.accel_x))
                logger.info("*** accel_y: " + str(sensordata.accel_y))
                logger.info("*** accel_z: " + str(sensordata.accel_z))
                
                # Convert the acceleration value in mg (milli-gees)
                if sensordata.accel_x != None:
                    sensordata.accel_x *= 3.9

                if sensordata.accel_y != None:
                    sensordata.accel_y *= 3.9

                if sensordata.accel_z != None:
                    sensordata.accel_z *= 3.9
            else:
                logger.info("Invalid resource: " + res)
            logger.info(payload)
        
        logger.info("Acquisition completed successfully")
        status = True

    # If an exception is raised, ip will be excluded from the dictionary.
    except coapException.coapTimeout as ex:
        logger.warning('GET request to "{0}" timed out ({1})'.format(request_uri, ex))
        if redis:
            error = "Request to " + request_uri + " timed out<br/>"
    except coapException.coapException as ex:
        logger.error('GET request to "{0}" failed ({1})'.format(request_uri, ex))
        if redis:
            error = "Request to " + request_uri + " failed: " + repr(e) + "<br/>"
    except Exception as ex:
        logger.error("An error has occurred: " + str(ex))
    finally:
        # Close the socket
        try:
            coap_obj.close()
            logger.info("CoAP socket closed")
        except Exception as ex:
            pass
            #logger.warning("CoAP socket cannot be closed!")
    if status:
        return {mote_ipv6: sensordata.__dict__}, error
    else:
        return None, error


