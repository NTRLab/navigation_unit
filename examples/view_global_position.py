#!/usr/bin/env python3

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
import threading
import time
from utils import main_utils, param_utils 

connection = None
need_reboot = False


def check_and_set_param(param, param_id, param_value):
    global need_reboot
    if param.param_id != param_id:
        return
    remote_value = param_utils.decode_param(param)

    if isinstance(remote_value,int):
        differ = (remote_value != param_value)
    else:
        differ = (abs(remote_value - param_value) > 0.001)

    if differ:
        param_utils.set_parameter(connection, param_id, param_value)
        need_reboot = True


stamp_offset_ms = None


def send_attitude():
    global stamp_offset_ms
    while True:
        stamp = int(time.time() * 1000) + stamp_offset_ms
        connection.mav.attitude_send(stamp, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        time.sleep(0.05)


if __name__ == '__main__':
    connection = main_utils.connect()
    main_utils.start_sending_heartbeat(connection)

    connection.wait_heartbeat()
    params = param_utils.list_params(connection)
    for p in params:
        print('Param %s = %3.6f' % (p.param_id, p.param_value))
        check_and_set_param(p, 'SAVE_MAP', 0)
        check_and_set_param(p, 'LOAD_MAP', 0)
        check_and_set_param(p, 'SEND_ORIGIN', 0)
        check_and_set_param(p, 'INIT_ALT', 1.0)

    if need_reboot:
        print('Parameters was changed. Rebooting, please wait...')
        main_utils.reboot(connection)
        main_utils.stop_sending_heartbeat(connection)
        del connection
        time.sleep(5)
        connection = main_utils.connect()
        main_utils.start_sending_heartbeat(connection)
        connection.wait_heartbeat()
        print('Got heartbeat.')

    sys_time_msg = connection.recv_match(type='SYSTEM_TIME', blocking=True)
    now_us = int(time.time() * 1e6)
    time_diff_us = sys_time_msg.time_unix_usec - now_us
    boot_offset_us = sys_time_msg.time_boot_ms * 1000 - sys_time_msg.time_unix_usec
    stamp_offset_ms = int((time_diff_us + boot_offset_us) / 1000)
    print('Stamp offset is %d ms' % stamp_offset_ms)

    attitude_thread = threading.Thread(target=send_attitude, daemon=True)
    attitude_thread.start()

    main_utils.send_command(
        connection,
        mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        param1=float(mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT),
        param2=1e6
    )

    print('Press Ctrl-C to terminate receiving global position messages.')
    try:
        while True:
            msg = connection.recv_match(type=['HEARTBEAT', 'GLOBAL_POSITION_INT', 'STATUSTEXT'], blocking=True)
            if msg.get_type() == 'HEARTBEAT':
                old_state = msg.system_status
                if msg.system_status == mavlink.MAV_STATE_EMERGENCY:
                    print("*** NO COORDINATES ***")
                elif msg.system_status == mavlink.MAV_STATE_CRITICAL:
                    print("*** ONLY ALTITUDE ***")
                elif msg.system_status == mavlink.MAV_STATE_STANDBY:
                    print("*** FULL COORDINATES ***")
                else:
                    print("*** UNEXPECTED SYSTEM STATUS (%d) ***" % msg.system_status)

            elif msg.get_type() == 'GLOBAL_POSITION_INT':
                print('Global Position message received (ms,lat,lon,alt,rel_alt,vx,vy,vz,hdg): %d, %.5f, %.5f, %.3f,'
                      ' %.3f, %.3f, %.3f, %.3f, %.3f' %
                      (msg.time_boot_ms, msg.lat/1e7, msg.lon/1e7, msg.alt/1e3, msg.relative_alt, msg.vx, msg.vy, msg.vz, msg.hdg)
                      )
            elif msg.get_type() == 'STATUSTEXT':
                main_utils.handle_statustext(connection, msg)
            else:
                print('Unexpected message %s' % msg.get_type())
    except KeyboardInterrupt:
        exit(0)
