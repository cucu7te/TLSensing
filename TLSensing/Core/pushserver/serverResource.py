"""
@author: Giacomo Donato Cascarano <gd.cascarano@gmail.com>
    
This module defines the CoAP resource called when CoAP push server receives data from motes.
    
@date: July 15

"""

import struct

import binascii
import socket

from coap import coapResource as r
from coap import coapDefines as d

from Core.motes.motes import compute_results
from Core.motes.motes import SensorData
from Core.models import Mote
from Core.models import Measure

import Core.motes.sensor_constants as c
import Core.pushserver.pushserver_constants as pc


"""
    Payload format:
    humidity        :    4 byte
    temp            :    4 byte
    datavalid       :    1 byte
    light           :    4 byte
    datavalid       :    1 byte
    acceleration:
        x           :    2 byte
        y           :    2 byte
        z           :    2 byte
    datavalid       :    1 byte
    infoBoardLength :    1 byte
    boardname       :    infoBoardLength byte
    moteIP          :    2 byte
"""

class serverResource(r.coapResource):
    def __init__(self, path):
        # Initialize parent class
        r.coapResource.__init__(self, path)
    
    #=================== reimplemented methods ==========================
    
    def POST(self, options=[], payload=None):
        (parserException, moteIP, data) = _payloadParser(payload)
        if parserException == pc.NO_EXCEPTION:
            _updateMote(moteIP, data)
            respCode        = d.COAP_RC_2_03_VALID
            respOptions     = []
            respPayload     = []#[ord(b) for b in out]
        elif parserException == pc.WRONG_IP:
	    if pc._verbose:
                print 'WRONG_IP ', moteIP
            respCode        = d.COAP_RC_4_06_NOTACCEPTABLE
            respOptions     = []
            respPayload     = [ord(b) for b in 'Wrong IP']
        else:
	    if pc._verbose:
                print 'Wrong payload format'
            respCode        = d.COAP_RC_4_06_NOTACCEPTABLE
            respOptions     = []
            respPayload     = [ord(b) for b in 'Wrong payload format']
        return (respCode,respOptions,respPayload)


def _payloadParser(payload=None):
    """Parse payload.
        @param payload
        
        @return parserException: parsing status code:
                                - NO_EXCEPTION: all right;
                                - WRONG_IP: wrong IP format or IP not in db;
                                - WRONG_PAYLOAD: generic payload format error.
        @return moteIP: complete sender IP. If the sender IP is not in the db returns an empty string.
        @return data: received data. See SensorData model for more information.
        """
    # Payload parser. Return sensor type and value.
    try:
        data = SensorData()
        moteIP = ''

        #if len(payload) != 30:
        #    raise struct.error

        # Read IP
    	infoBoardLength = ord(bytearray(payload[pc.BOARD_NAME_LENGTH_START:pc.BOARD_NAME_LENGTH_END]))
        rawIP = binascii.hexlify(bytearray(payload[pc.BOARD_NAME_LENGTH_END+infoBoardLength:pc.BOARD_NAME_LENGTH_END+infoBoardLength+2]))
        board_name = struct.unpack_from('={0}s'.format(infoBoardLength), bytearray(payload[pc.BOARD_NAME_LENGTH_END:pc.BOARD_NAME_LENGTH_END+infoBoardLength]))[0]
        print "* infoBoardLength: " + str(infoBoardLength)
        print "* rawIP: " + str(rawIP)
        print "* board_name: " + str(board_name)

        import pdb
        pdb.set_trace()
        if board_name == pc.telosb_boardname:
            moteIP = '{0}{1}'.format(pc.telosb_prefix, rawIP)
        elif board_name == pc.cc2538_boardname:
            moteIP = '{0}{1}'.format(pc.cc2538_prefix, rawIP)
        else:
            raise Mote.DoesNotExist

        # Load last data (no exception ==> ip is in the db and ==> it is valid)
        mote = Mote.objects.get(ipv6=moteIP)
        if len(mote.measures) == 0:
            last_measure = Measure()
            last_measure.accel_x = 0.0
    	    last_measure.accel_y = 0.0
    	    last_measure.accel_z = 0.0
    	    last_measure.light = 0.0
    	    last_measure.temperature = 0.0
    	    last_measure.humidity = 0.0
        else:
            last_measure = mote.measures[-1]

        if pc._verbose:
            print 'POST received from {0}: {1}'.format(board_name, rawIP)

        # Read data
        if struct.unpack_from('=?', bytearray(payload[pc.TEMP_HUM_VALID_START:pc.TEMP_HUM_VALID_END]))[0]:
            # Hum/Temp valid
            (data.humidity, data.temperature) = struct.unpack_from('=ff', bytearray(payload[pc.HUM_START:pc.TEMP_END]))
	    # Set last data
            if data.temperature == -274.0:
                # Hum valid
                data.temperature = last_measure.temperature
                if pc._verbose:
                    print 'Hum:\t{0}\n'.format(data.humidity)
            else:
                # Temp valid
                data.humidity = last_measure.humidity
                if pc._verbose:
                    print 'Temp:\t{0}\n'.format(data.temperature)
            data.light = last_measure.light
            if board_name == pc.cc2538_boardname:
	        (data.accel_x, data.accel_y, data.accel_z) = (last_measure.accel_x, last_measure.accel_y, last_measure.accel_z)
        elif struct.unpack_from('=?', bytearray(payload[pc.LIGHT_VALID_START:pc.LIGHT_VALID_END]))[0]:
            # Light valid
            data.light = struct.unpack_from('=f', bytearray(payload[pc.LIGHT_START:pc.LIGHT_END]))[0]
            if pc._verbose:
      	        print 'Light:\t{0}\n'.format(data.light)
            # Set last data
            (data.humidity, data.temperature) = (last_measure.humidity, last_measure.temperature)
            if board_name == pc.cc2538_boardname:
                (data.accel_x, data.accel_y, data.accel_z) = (last_measure.accel_x, last_measure.accel_y, last_measure.accel_z)
        elif struct.unpack_from('=?', bytearray(payload[pc.ACC_VALID_START:pc.ACC_VALID_END]))[0] and board_name == pc.cc2538_boardname:
            # Acc valid
            (data.accel_x, data.accel_y, data.accel_z) = struct.unpack_from('=hhh', bytearray(payload[pc.X_ACCELERATION_START:pc.Z_ACCELERATION_END]))
            data.accel_x *= 3.9
            data.accel_y *= 3.9
            data.accel_z *= 3.9
            if pc._verbose:
      	        print 'X:\t{0}\nY:\t{1}\nZ:\t{2}\n'.format(data.accel_x, data.accel_y, data.accel_z)
            # Set last data
            (data.humidity, data.temperature, data.light) = (last_measure.humidity, last_measure.temperature, last_measure.light)
        else:
            raise struct.error
        parserException = pc.NO_EXCEPTION
    except Mote.DoesNotExist:
    	moteIP = rawIP
        parserException = pc.WRONG_IP
    except struct.error:
        parserException = pc.WRONG_PAYLOAD
    return (parserException, moteIP, data)


def _updateMote(moteIP, data):
    # Update the dictionary
    # Round measure values before saving
    for key, value in data.__dict__.items():
        data.__dict__[key] = round(value, 2)
    try:
        mote = Mote.objects.get(ipv6=moteIP)
        mote.measures.append(Measure(**(data.__dict__)))
        mote.save()
        motes.compute_results(moteIP)
    except Mote.DoesNotExist:
        pass
    return


