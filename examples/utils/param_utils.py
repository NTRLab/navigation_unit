#    Copyright 2020, NTRobotics
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from pymavlink import mavutil
from pymavlink.mavutil import mavlink
import struct
from utils import main_utils

def decode_param(param):
    if param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT8:
        return struct.unpack('>xxxB', struct.pack('>f', param.param_value))[0]
    elif param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT8:
        return struct.unpack('>xxxb', struct.pack('>f', param.param_value))[0]
    elif param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT16:
        return struct.unpack('>xxH', struct.pack('>f', param.param_value))[0]
    elif param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT16:
        return struct.unpack('>xxh', struct.pack('>f', param.param_value))[0]
    elif param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT32:
        return struct.unpack('>I', struct.pack('>f', param.param_value))[0]
    elif param.param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT32:
        return struct.unpack('>i', struct.pack('>f', param.param_value))[0]
    else:
        return param.param_value

def encode_param(param_value, param_type=mavutil.mavlink.MAV_PARAM_TYPE_REAL32):
    if param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT8:
        return struct.unpack('>f', struct.pack('>xxxB', int(param_value)))[0]
    elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT8:
        return struct.unpack('>f', struct.pack('>xxxb', int(param_value)))[0]
    elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT16:
        return struct.unpack('>f', struct.pack('>xxH', int(param_value)))[0]
    elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT16:
        return struct.unpack('>f', struct.pack('>xxh', int(param_value)))[0]
    elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT32:
        return struct.unpack('>f', struct.pack('>I', int(param_value)))[0]
    elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT32:
        return struct.unpack('>f', struct.pack('>i', int(param_value)))[0]
    else:
        return float(param_value)

def list_params(connection):
    connection.mav.param_request_list_send(
        connection.target_system,
        connection.target_component
    )

    params = list()
    while True:
        message = connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=1)
        if message is None:
            break
        params.append(message)

    return params

def set_parameter(connection, param_id, param_value):
    connection.mav.param_request_read_send(
        connection.target_system,
        connection.target_component,
        param_id.encode('UTF-8'),
        -1
    )
    while True:
        msg = connection.recv_match(type=['PARAM_VALUE', 'STATUSTEXT'], blocking=True)
        if msg.get_type() == 'PARAM_VALUE':
            if msg.param_id == param_id:
                param = msg
                break
        elif msg.get_type() == 'STATUSTEXT':
            main_utils.handle_statustext(connection, msg)
            if (str(msg.text[:17]) == "Unknown parameter"):
                return

    try:
        connection.mav.param_set_send(
            connection.target_system,
            connection.target_component,
            param_id.encode('UTF-8'),
            encode_param(param_value, param.param_type),
            param.param_type
        )
    except ValueError:
        print('Invalid value type')
        return

    cond = 'PARAM_VALUE.param_id=="%s"' % param_id
    while True:
        msg = connection.recv_match(type=['PARAM_VALUE', 'STATUSTEXT'], blocking=True)
        if msg.get_type() == 'PARAM_VALUE':
            if msg.param_id == param_id:
                print('Parameter %s was set to %s' % (msg.param_id, str(decode_param(msg))))
                return
        if msg.get_type() == 'STATUSTEXT':
            main_utils.handle_statustext(connection, msg)
