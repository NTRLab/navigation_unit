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
from utils import main_utils

if __name__ == '__main__':
    try:
        connection = main_utils.connect()
        main_utils.start_sending_heartbeat(connection)

        connection.wait_heartbeat()

        success = main_utils.reboot(connection)

        print('reboot: %r' % (success))
    except KeyboardInterrupt:
        exit(0)
