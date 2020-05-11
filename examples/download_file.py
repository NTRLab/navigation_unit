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

import struct
from utils import main_utils, ftp_utils
from crccheck.crc import Crc32

connection = None


def list_dir(dir_name):
    dir_offset = 0

    entries_list = list()
    while True:
        response = ftp_utils.send_ftp_msg(
            connection,
            session = 1,
            opcode = ftp_utils.OP_ListDirectory,
            offset = dir_offset,
            data = bytearray(dir_name, 'ascii'),
            wait_resp = True
        )

        payload_header = ftp_utils.extract_header(response)
        (opcode, size) = ftp_utils.parse_header(payload_header)[2:4]
        data = ftp_utils.extract_data(response, size)
        if opcode == ftp_utils.OP_Nack:
            if data[0] == ftp_utils.ERR_EndOfFile:
                break
            else:
                return

        entries = data.split(b'\x00')
        for entry in entries:
            if len(entry) == 0:
                continue
            dir_offset += 1
            entry = str(entry, 'ascii')
            if entry[0] == 'D':
                entries_list.append(' D %s' % entry[1:])
            elif entry[0] == 'F':
                entries_list.append('   %s' % entry[1:])
            else:
                entries_list.append(entry)

    return entries_list


def get_file(filename):
    response = ftp_utils.send_ftp_msg(
        connection,
        session = 2,
        opcode = ftp_utils.OP_OpenFileRO,
        data = bytearray(filename, 'ascii'),
        wait_resp=True
    )

    payload_header = ftp_utils.extract_header(response)
    (opcode, size) = ftp_utils.parse_header(payload_header)[2:4]
    if opcode == ftp_utils.OP_Nack:
        print(ftp_utils.parse_error(response))
        return

    try:
        data = ftp_utils.extract_data(response, size)
        (filesize,) = struct.unpack("<I", data)

        ftp_utils.send_ftp_msg(
            connection,
            session = 2,
            opcode = ftp_utils.OP_BurstReadFile,
            data = bytearray(),
            wait_resp=False
        )

        f = open(filename, mode='wb')

        try:
            burst_offset = 0

            while True:
                response = ftp_utils.wait_for_response(connection, 2, ftp_utils.OP_BurstReadFile)
                payload_header = ftp_utils.extract_header(response)
                (opcode, size, _, burst_complete, _, offset) = ftp_utils.parse_header(payload_header)[2:8]
                if opcode == ftp_utils.OP_Nack:
                    return

                if offset < burst_offset:
                    continue

                if offset > burst_offset:
                    ftp_utils.send_ftp_msg(
                        connection,
                        session = 2,
                        opcode = ftp_utils.OP_BurstReadFile,
                        offset = burst_offset,
                        data = bytearray(),
                        wait_resp=False
                    )
                    continue

                data = ftp_utils.extract_data(response, size)
                f.write(data)
                burst_offset += len(data)

                print('\r%u/%u Bytes (%3.1f%%)' % (burst_offset, filesize, burst_offset / filesize * 100.), end='')

                if burst_complete == 1:
                    print()
                    break

        finally:
            f.close()

    finally:
        ftp_utils.send_ftp_msg(
            connection,
            session = 2,
            opcode = ftp_utils.OP_TerminateSession,
            data = bytearray(),
            wait_resp = True
        )

    if ftp_utils.check_crc(connection, filename, filename):
        print('File %s downloaded succesfull' % filename)
    else:
        print('File %s downloaded with errors' % filename)


if __name__ == '__main__':
    try:
        connection = main_utils.connect()
        main_utils.start_sending_heartbeat(connection)

        connection.wait_heartbeat()

        files = list_dir('/')
        print('Files: %s' % len(files))
        for f in files:
            print(f)

        requested_file = input('Choose file to download: ')
        get_file(requested_file)
    except KeyboardInterrupt:
        print
