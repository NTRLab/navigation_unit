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
from utils import main_utils, ftp_utils

connection = None


def send_chunk(session, chunk, offset):
    response = ftp_utils.send_ftp_msg(
        connection,
        session = session,
        opcode = ftp_utils.OP_WriteFile,
        offset = offset,
        data = chunk,
        wait_resp=True
    )
    
    payload_header = ftp_utils.extract_header(response)
    (opcode, size) = ftp_utils.parse_header(payload_header)[2:4]
    if opcode == ftp_utils.OP_Ack:
        return True
    else:
        if size != 0:
            error_code = response.payload[12]
            print("Error code: %u" % error_code)
        else:
            print("Unknown error")
        return False


def send_file(source, target):
    session_id = 1
    
    response = ftp_utils.send_ftp_msg(
        connection,
        session = session_id,
        opcode = ftp_utils.OP_CreateFile,
        data = bytearray(target, 'ascii'),
        wait_resp=True
    )
    payload_header = ftp_utils.extract_header(response)
    (opcode, size) = ftp_utils.parse_header(payload_header)[2:4]
    if opcode != ftp_utils.OP_Ack:
        print("Can't create file!")
        print(ftp_utils.parse_error(response))
        return
    try:
        f = open(source, mode='rb')
        try:
            content = f.read()
        finally:
            f.close()
        filesize = len(content)
        for offset in range(0, len(content), ftp_utils.MAX_Payload):
            chunk_end = min((offset+ftp_utils.MAX_Payload, filesize))
            chunk = bytearray(content[offset:chunk_end])
            chunk_transmitted = False
            while not chunk_transmitted:
                chunk_transmitted = send_chunk(session_id, chunk, offset)
            print('\r%u/%u Bytes (%3.1f%%)' % (chunk_end, filesize, chunk_end / filesize * 100), end='')
    finally:
        ftp_utils.send_ftp_msg(
            connection,
            session = session_id,
            opcode = ftp_utils.OP_TerminateSession,
            data = bytearray(),
            wait_resp=False
        )
        print()
    if ftp_utils.check_crc(connection, source, target):
        print('File %s uploaded succesfull' % (target))
    else:
        print('File %s uploaded with errors' % (target))

if __name__ == '__main__':
    try:
        connection = main_utils.connect()
        main_utils.start_sending_heartbeat(connection)

        connection.wait_heartbeat()

        filename = input('Path to source file: ')
        remote_filename = input('Path to target file: ')
        send_file(filename, remote_filename)
    except KeyboardInterrupt:
        print()