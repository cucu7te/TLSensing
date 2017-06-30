"""
@author: Giacomo Donato Cascarano <gd.cascarano@gmail.com>
    
This module defines some constants used in the pushServer module.
    
@date: July 15
"""

# Verbose
_verbose = True

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


# Payload bounds:
HUM_START = 0
HUM_END = HUM_START + 4
TEMP_START = HUM_END
TEMP_END = TEMP_START + 4
TEMP_HUM_VALID_START = TEMP_END
TEMP_HUM_VALID_END = TEMP_HUM_VALID_START + 1
LIGHT_START = TEMP_HUM_VALID_END
LIGHT_END = LIGHT_START + 4
LIGHT_VALID_START = LIGHT_END
LIGHT_VALID_END = LIGHT_VALID_START + 1
X_ACCELERATION_START = LIGHT_VALID_END
X_ACCELERATION_END = X_ACCELERATION_START + 2
Y_ACCELERATION_START = X_ACCELERATION_END
Y_ACCELERATION_END = Y_ACCELERATION_START + 2
Z_ACCELERATION_START = Y_ACCELERATION_END
Z_ACCELERATION_END = Z_ACCELERATION_START + 2
ACC_VALID_START = Z_ACCELERATION_END
ACC_VALID_END = ACC_VALID_START + 1
BOARD_NAME_LENGTH_START = ACC_VALID_END
BOARD_NAME_LENGTH_END = BOARD_NAME_LENGTH_START + 1

# payloadParser exception
NO_EXCEPTION = 0
WRONG_PAYLOAD = 1
WRONG_IP = 2

# IP prefix
telosb_prefix = 'bbbb::1415:9200:15:'
cc2538_prefix = 'bbbb::12:4b00:433:'
#telosb_prefix = 'bbbb:0000:0000:0000:1415:9200:0015:'
#cc2538_prefix = 'bbbb:0000:0000:0000:0012:4b00:060d:'
#cc2538_prefix = 'bbbb:0000:0000:0000:0012:4b00:0433:'

# Board name
cc2538_boardname = 'CC2538';
telosb_boardname = 'TelosB';
