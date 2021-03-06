"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

#TODO: Rimuovere dopo find_all_sensors
HISTORY_MEASURES_NUMBER = 10


###############################################################################
#                   Constants for payload parsing
#
# The following constants are used to parse the payload returned
# by 'sensordata', an app for the OpenWSN platform
# (see https://github.com/openwsn-berkeley/openwsn-fw).
###############################################################################

# Upper and lower bounds for extracting the humidity value.
HUMIDITY_LOWER = 0
HUMIDITY_UPPER = HUMIDITY_LOWER + 4

# Upper and lower bounds for extracting the temperature value.
#####TEMPERATURE_LOWER = 4
TEMPERATURE_LOWER = 0
TEMPERATURE_UPPER = TEMPERATURE_LOWER + 4

# Index of the payload byte that indicates the presence of the
# temperature/humidity sensor.
TEMP_HUMID_ISPRESENT_INDEX = 8

# Upper and lower bounds for extracting the light value.
#####LIGHT_LOWER = 9
LIGHT_LOWER = 0
LIGHT_UPPER = LIGHT_LOWER + 4

# Index of the payload byte that indicates the presence of the light sensor.
LIGHT_ISPRESENT_INDEX = 13

# Upper and lower bounds for extracting the acceleration values.
#####ACCEL_LOWER = 14
ACCEL_LOWER = 0
ACCEL_X_UPPER = ACCEL_LOWER + 2
ACCEL_Y_UPPER = ACCEL_X_UPPER + 2
ACCEL_Z_UPPER = ACCEL_Y_UPPER + 2

# Index of the payload byte that indicates the presence of the
# accelerometer.
ACCEL_ISPRESENT_INDEX = 20

###############################################################################
#                   Constants for sensor querying
###############################################################################

# CoAP resource installed by the app.
SENSORDATA_RES = '/sens'

# Uri-Query arguments.
# When sending a GET request to the app, a CoAP query string may be supplied
# with the following arguments, e.g.
# coap://[bbbb::12:4b00:433:ed36]/sens?temp&humid
#ACCEL_QUERY = 'accel'
#TEMPERATURE_QUERY = 'temp'
#HUMIDITY_QUERY = 'humid'
#LIGHT_QUERY = 'light'

ACCEL_QUERY = 'A'
TEMPERATURE_QUERY = 'T'
HUMIDITY_QUERY = 'H'
LIGHT_QUERY = 'L'

ALL_QUERY = [ACCEL_QUERY, TEMPERATURE_QUERY, HUMIDITY_QUERY, LIGHT_QUERY]
#ALL_QUERY = ['A','T','H','L']

# Default timeout values in seconds
#DEFAULT_ACK_TIMEOUT = 7
#DEFAULT_RESP_TIMEOUT = 10
DEFAULT_ACK_TIMEOUT = 3
DEFAULT_RESP_TIMEOUT = 6

###############################################################################
#                   Thresholds constants
#
# The following constants are used to set thresholds values when mote is
# signed up to TLSensing platform.
###############################################################################

OPENMOTE_THRESHOLD_VALUES = {
    "accel_x": {
        "max": {
            "val": 16000,
            "msg": "Max threshold (OpenMote) (accel_x)"
        },
        "min": {
            "val": -16000,
            "msg": "Min threshold (OpenMote) (accel_x)"
        }
    },
    "accel_y": {
        "max": {
            "val": 16000,
            "msg": "Max threshold (OpenMote) (accel_y)"
        },
        "min": {
            "val": -16000,
            "msg": "Min threshold (OpenMote) (accel_y)"
        }
    },
    "accel_z": {
        "max": {
            "val": 16000,
            "msg": "Max threshold (OpenMote) (accel_z)"
        },
        "min": {
            "val": -16000,
            "msg": "Min threshold (OpenMote) (accel_z)"
        }
    },
    "light": {
        "max": {
            "val": 188000,
            "msg": "Max threshold (OpenMote) (light)"
        },
        "min": {
            "val": 0.045,
            "msg": "Min threshold (OpenMote) (light)"
        }
    },
    "temperature": {
        "max": {
            "val": 125,
            "msg": "Max threshold (OpenMote) (temperature)"
        },
        "min": {
            "val": -40,
            "msg": "Min threshold (OpenMote) (temperature)"
        }
    },
    "humidity": {
        "max": {
            "val": 100,
            "msg": "Max threshold (OpenMote) (humidity)"
        },
        "min": {
            "val": 0,
            "msg": "Min threshold (OpenMote) (humidity)"
        }
    }
}

TELOSB_THRESHOLD_VALUES = {
    "light": {
        "max": {
            "val": 188000,
            "msg": "Max threshold (TelosB) (light)"
        },
        "min": {
            "val": 0.045,
            "msg": "Min threshold (TelosB) (light)"
        }
    },
    "temperature": {
        "max": {
            "val": 125,
            "msg": "Max threshold (TelosB) (temperature)"
        },
        "min": {
            "val": -40,
            "msg": "Min threshold (TelosB) (temperature)"
        }
    },
    "humidity": {
        "max": {
            "val": 100,
            "msg": "Max threshold (TelosB) (humidity)"
        },
        "min": {
            "val": 0,
            "msg": "Min threshold (TelosB) (humidity)"
        }
    }
}

DEFAULT_THRESHOLDS = {
    "OpenMote": OPENMOTE_THRESHOLD_VALUES,
    "TelosB": TELOSB_THRESHOLD_VALUES
}
