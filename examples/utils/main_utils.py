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

import threading
import time
from pymavlink.mavutil import mavlink, mavlink_connection

def _send_heartbeat(connection, armed=False):
    base_mode = 0b10000000 if armed else 0b00000000
    while connection._ntr_sending_heartbeat:
        connection.mav.heartbeat_send(mavlink.MAV_TYPE_GCS, mavlink.MAV_AUTOPILOT_INVALID, base_mode, 0, 0)
        time.sleep(1)

def start_sending_heartbeat(connection, armed=False):
    connection._ntr_sending_heartbeat = True
    connection._ntr_heartbeat_thread = threading.Thread(target=_send_heartbeat, args=(connection, armed,), daemon=True)
    connection._ntr_heartbeat_thread.start()

def stop_sending_heartbeat(connection):
    connection._ntr_sending_heartbeat = False
    connection._ntr_heartbeat_thread.join()

def send_command(connection, command, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0, blocking=False):
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        command, confirmation=0,
        param1=param1, param2=param2, param3=param3, param4=param4, param5=param5, param6=param6, param7=param7
    )

    if blocking:
        response = connection.recv_match(type='COMMAND_ACK', condition=('COMMAND_ACK.command == %d' % command), blocking=True)
        return response.result

def reboot(connection):
    result = send_command(connection, mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, blocking=True, param2=1)
    return (result == mavlink.MAV_RESULT_ACCEPTED)

def shutdown(connection):
    result = send_command(connection, mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, blocking=True, param2=2)
    return (result == mavlink.MAV_RESULT_ACCEPTED)

def connect():
    f = open('navblock_ip.txt')
    try:
        ip = f.read()
    finally:
        f.close()

    return mavlink_connection('udpout:%s:14540' % (ip), source_system=1, source_component=0, dialect='common')

def handle_statustext(connection, msg):
    if msg.get_type() != 'STATUSTEXT':
        raise TypeError('Wrong type of message')

    if not connection.mavlink20():
        print(msg.text)
        return

    if msg.id == 0:
        print(msg.text)
        return

    try:
        connection._ntr_statustext_buffer[msg.id][msg.chunk_seq] = msg.text
    except AttributeError:
        connection._ntr_statustext_buffer = { msg.id: { msg.chunk_seq: msg.text } }
    except KeyError:
        connection._ntr_statustext_buffer[msg.id] = { msg.chunk_seq: msg.text }

    if len(msg.text) < 50:
        msg_sequence = connection._ntr_statustext_buffer[msg.id]
        text = ''
        prev_chunk_seq = min(msg_sequence) - 1
        if prev_chunk_seq != -1:
            text += '{...}'
        for chunk_seq in sorted(msg_sequence):
            if (prev_chunk_seq + 1) != chunk_seq:
                text += '{...}'
            text += msg_sequence[chunk_seq]
            prev_chunk_seq = chunk_seq
        print()
        print(text)
        connection._ntr_statustext_buffer.pop(msg.id)
