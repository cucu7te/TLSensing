"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
@contributor: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import json

def publish_message(message, channel="tls_update", broadcast=True):
    """
    Publishes a message to Redis queue.

    @param message: a dict, to be json dumped, to store data to be passed to web socket
    @param channel: the channel whose clients subscribe
    @param broadcast: if the message needs to be received by all motes
    """
    try:    
        redis_publisher = RedisPublisher(facility=channel, broadcast=broadcast)
        message = RedisMessage(json.dumps(message))
        # and somewhere else
        redis_publisher.publish_message(message)
    except Exception, e:
        print repr(e)

# from Core.models import Mote
# from Core.settings import settings
# from django.conf import settings as djangosettings
# from Core.motes.motes import check_thresholds

# ###########################################################

# from Core.models import MetaModel
# from Core.models import MoteBackup
# from Core.models import Notification
# from Core.models import Threshold
# from Core.sensor.charts import chart
# from TLSensing.settings import CHART_URL
# from sensor.sensor_constants import HISTORY_MEASURES_NUMBER
# import numpy

# from coap import coap
# from coap import coapException

# import socket
# import os

# import logging
# logger = logging.getLogger(__name__)

# ######################################################################################################

# #TODO: Non eliminare ancora, devo vedere col pushserver
# # def compute_mote_results(n_measures=HISTORY_MEASURES_NUMBER, gotMotes={}):
# #     """
# #     Control the post-aquisition process and send updated data to messages queue.

# #     @param n_measures: points to be plotted out
# #     """
# #     if len(gotMotes) > 0:
# #         motes = []
# #         allMotes = find_all_sensors(n_measures)
# #         for gm in gotMotes:
# #             for m in allMotes:
# #                 if m.ipv6 == gm:
# #                     motes.append(m)
# #                     break
# #     else:
# #         motes = find_all_sensors(n_measures)

# #     if motes:
# #         chart(motes, n_measures)

# def compute_mote_result(mote_ipv6):
#     """
#     Control the post-aquisition process and send updated data to messages queue.

#     @param n_measures: points to be plotted out
#     """

#     # Generating charts
#     logger.info("Generating charts")
#     chart(mote_ipv6, int(settings.read()["sampledmeasures"]))

#     # Checking for thresholds
#     logger.info("Checking thresholds")
#     for ip in mote_ipv6:
#         mote = Mote.objects(ipv6=ip).fields(slice__measures=-1)[0]
#         check_thresholds([mote])

# ################################################
# ## WASTEBIN

# # TODO: Non rimuovere ancora, devo vedere per il pannello di controllo
# # def add_sensor(data):
# #     """
# #     Add a new sensor to testbed enviroment if the ipv6 address is not already associated
# #     to any sensor.
# #     The function assigns a fixed alias name if none is provided.

# #     @param data: a dict contains form data
# #     @raise socket.error: if the IPv6 address string is invalid
# #     @return the list of registered motes
# #     """
# #     try:
# #         # If data["ipv6"] is not a valid IPv6 address string,
# #         # this call will raise socket.error.
# #         socket.inet_pton(socket.AF_INET6, data["ipv6"])

# #         mote = Mote()
# #         mote.thresholds = Threshold()
# #         mote.thresholds.set_thresholds(mote_type=data["mote_type"])
# #         mote.alias_name = None
# #         if data["alias_name"]:
# #             mote.alias_name = data["alias_name"].replace(' ','_')  #modify to replace space caracter with '_' to evit problem
# #         else:
# #             mote.alias_name = "No_alias_named_mote"                #modify to replace space caracter with '_' to evit problem

# #         mote.ipv6 = data["ipv6"]
# #         mote.mote_type = data["mote_type"]
# #         mote.save()
# #         return Mote.objects
# #     except socket.error:
# #         # Invalid IPV6 address. Should be handled by the caller.
# #         raise
# #     except Exception as e:
# #         logger.error("Generic exception while adding sensor: %s; passed data is: %s" %(str(e)," ".join(["%s:%s" %(key,data[key]) for key in data.keys()])))
# #         return None

# #TODO: Come sopra
# # def remove_sensor(mote, data):
# #     """
# #     Remove sensor from testbed;
# #     If <data> contains the "remove_data" key, related measures mote will be deleted too.
# #     Otherwise the mote will be disabled (and so, not visible onto the TLSensing web page)

# #     @param data: the dict whose "remove_data" key needs to be exctracted by
# #     @param mote: the mote whose needs to be disabled or removed
# #     @return the updated list of motes
# #     """

# #     try:
# #         # if "remove_data" in data:
# #         #     #check for generated charts and remove them
# #         #     if mote.base_chart:
# #         #         os.remove(os.path.join(CHART_URL, "mote_base-%s.svg" %(mote.id)))
# #         #     if mote.acc:
# #         #         os.remove(os.path.join(CHART_URL, "mote_acc-%s.svg" %(mote.id)))
# #         #     if mote.acc_details:
# #         #         os.remove(os.path.join(CHART_URL, "mote_acc_details-%s.svg" %(mote.id)))
# #         #     mote.delete()
# #         # else:
# #         #     mote.disabled = True
# #         # mote.save()
# #         logger.info("Removing mote " + mote["ipv6"])
# #         motebackup = MoteBackup()
# #         motebackup["ipv6"] = mote["ipv6"]
# #         motebackup["alias_name"] = mote["alias_name"]
# #         motebackup["measures"] = mote["measures"]
# #         motebackup["mote_type"] = mote["mote_type"]
# #         motebackup["thresholds"] = mote["thresholds"]
# #         mote.delete()
# #         motebackup.save()
# #         return Mote.objects
# #     except Exception as e:
# #         logger.error("Generic exception while removing mote: %s; passed data is: %s" %(str(e)," ".join(["%s:%s" %(key,data[key]) for key in data.keys()])))
# #         return None

# #TODO: Rimuovere quando levo mote_object
# def find_all_sensors(n_measures=HISTORY_MEASURES_NUMBER):
#     """
#     Return all motes registered to the platform, not disabled with a minimal amount of data.
#     The number of retrieved feature is given by the <n_measures> argument.
#     Compute additional details using the MongoDB Aggregation Framework and add them to the mote entity.

#     @param n_measures (default: HISTORY_MEASURES_NUMBER): number of related measures to be retrieved
#     @return the list of motes, along with their additional informations
#     """
#     motes_new = []
#     try:
#         motes = Mote.objects.filter(disabled__ne=True).fields(slice__measures=-n_measures)
#         motes_info = Mote.objects.exec_js(AGGREGATION_QUERY)
#         if "_firstBatch" in motes_info:
#             key = "_firstBatch"
#         else:
#             key= "result"
#         if key in motes_info and motes_info[key]:
#             for mote in motes:
#                 _tmp = filter(lambda item: item["_id"] == mote.id , motes_info[key])
#                 if _tmp:
#                     mote.meta_model = MetaModel(_tmp[0])
#                 motes_new.append(mote)
#             return check_thresholds(motes_new)
#         return check_thresholds(motes)
#     except Exception as e:
#         logger.error("Generic exception while finding all motes and computing additional values: %s" %str(e))
#         return None

# from ws4redis.publisher import RedisPublisher
# from ws4redis.redis_store import RedisMessage
# import json