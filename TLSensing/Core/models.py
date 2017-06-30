"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

from mongoengine import FloatField, StringField, BooleanField
from mongoengine import ListField, EmbeddedDocumentField, DateTimeField, DictField
from mongoengine import EmbeddedDocument, Document
from TLSensing.settings import CHART_URL
from Core.motes.sensor_constants import DEFAULT_THRESHOLDS

import datetime
import os
import logging
logger = logging.getLogger("Core.services")

#{"statid": statid, "data": sorted(table_data["data"], key=lambda k: k["measure_type"], reverse=True)}
class Stats(Document):
    meta = {'collection': 'motestats'}
    statid = StringField()
    data = DictField()

    def as_dict(self):
        data = self.__dict__["_data"]
        return {field: data[field] for field in data if data[field] != {}}

class Threshold(EmbeddedDocument):
    """
    Map Threshold document to application level,
    Values are set on constructor method.
    """
    accel_x = DictField()
    accel_y = DictField()
    accel_z = DictField()
    light = DictField()
    temperature = DictField()
    humidity = DictField()

    def as_dict(self):
        data = self.__dict__["_data"]
        return {field: data[field] for field in data if data[field] != {}}

    def get(self, mote_type):
        data = {}
        for mt in DEFAULT_THRESHOLDS[mote_type]:
            data[mt] = getattr(self, mt)
        return data

    def set(self, threshold, mote_type):
        try:
            for mt in DEFAULT_THRESHOLDS[mote_type]:
                print str(mt) + " " + str(threshold[mt])
                setattr(self, mt, threshold[mt]);
            return True
        except Exception as e:
            print repr(e)
            logger.error("Exception setting default threshold values for %s \
                 mote; exception is: %s" % (mote_type, str(e)))
            return False

class Measure(EmbeddedDocument):
    """Map measure document to application level."""
    date = DateTimeField(default=datetime.datetime.now)
    accel_x = FloatField()
    accel_y = FloatField()
    accel_z = FloatField()
    light = FloatField()
    temperature = FloatField()
    humidity = FloatField()

    def as_dict(self):
        return self.__dict__["_data"]

class Notification(EmbeddedDocument):
    date = DateTimeField(default=datetime.datetime.now)
    not_type = StringField()
    measure = StringField()
    message = StringField()

    def as_dict(self):
        return self.__dict__["_data"]

class MoteBackup(Document):
    meta = {'collection': 'motebackup'}
    ipv6 = StringField()
    alias_name = StringField()
    measures = ListField(EmbeddedDocumentField(Measure))
    mote_type = StringField()
    thresholds = EmbeddedDocumentField(Threshold)
    notifications = ListField(EmbeddedDocumentField(Notification))

class Mote(Document):
    """
    Map mote document to application level,
    defining some base properties.
    """
    ipv6 = StringField()
    alias_name = StringField()
    measures = ListField(EmbeddedDocumentField(Measure))
    mote_type = StringField()
    thresholds = EmbeddedDocumentField(Threshold)
    notifications = ListField(EmbeddedDocumentField(Notification))

    def as_dict(self):
        data = self.__dict__["_data"]
        data["thresholds"] = data["thresholds"].as_dict()
        data["measures"] = [meas.as_dict() for meas in data["measures"]]
        return data

    def chart_exists(self, chart_type):
        return os.path.isfile(os.path.join(CHART_URL, "mote_%s-%s.svg" %(chart_type, self.id)))

    def get_chart(self, chart_type):
        return open(os.path.join(CHART_URL, "mote_%s-%s.svg" %(chart_type, self.id)), "rb")
    
    @property
    def base_chart(self):
        """
        Check if base chart exist for the given mote.

        @return bool value to indicate if base chart exists or not
        """
        return os.path.isfile(
            os.path.join(CHART_URL, "mote_base-%s.svg" % (self.id)))

    @property
    def acc(self):
        """
        Check if 3D accelerometer values chart exist for the given mote.

        @return bool value to indicate if 3D accelerometer values
        chart exists or not
        """
        return os.path.isfile(
            os.path.join(CHART_URL, "mote_acc-%s.svg" % (self.id)))

    @property
    def acc_details(self):
        """
        Check if single accelerometer axis chart exist for the given mote.

        @return bool value to indicate if single accelerometer axis chart
        exists or not
        """
        return os.path.isfile(
            os.path.join(CHART_URL, "mote_acc_details-%s.svg" % (self.id)))

    def get_measures(self, measure_type="", n_measures=0):
        if measure_type != "":
            values = sorted([{"value": meas[measure_type], "date": meas["date"]} for meas in self.measures if meas[measure_type] != None], key=lambda k: k["date"])
        else:
            values = sorted([meas for meas in self.measures], key=lambda k: k["date"])

        if n_measures > 0:
            return values[-n_measures:]
        else:
            return values
