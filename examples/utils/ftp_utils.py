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

import struct
from crccheck.crc import Crc32

_ftp_seq = 0

# opcodes
OP_None = 0
OP_TerminateSession = 1
OP_ResetSessions = 2
OP_ListDirectory = 3
OP_OpenFileRO = 4
OP_ReadFile = 5
OP_CreateFile = 6
OP_WriteFile = 7
OP_RemoveFile = 8
OP_CreateDirectory = 9
OP_RemoveDirectory = 10
OP_OpenFileWO = 11
OP_TruncateFile = 12
OP_Rename = 13
OP_CalcFileCRC32 = 14
OP_BurstReadFile = 15
OP_Ack = 128
OP_Nack = 129

# error codes
ERR_None = 0
ERR_Fail = 1
ERR_FailErrno = 2
ERR_InvalidDataSize = 3
ERR_InvalidSession = 4
ERR_NoSessionsAvailable = 5
ERR_EndOfFile = 6
ERR_UnknownCommand = 7
ERR_FileExists = 8
ERR_FileProtected = 9
ERR_FileNotFound = 10

HDR_Len = 12
MAX_Payload = 239
HDR_Format = '<HBBBBBBI'

def extract_header(message):
    return bytearray(message.payload[:12])

def parse_header(header):
    parsed = struct.unpack(HDR_Format, header)
    global _ftp_seq
    _ftp_seq = parsed[0]
    return parsed

def extract_data(message, size=-1):
    if size == -1:
        header = extract_header(message)
        size = parse_header(header)[4]
    return bytearray(message.payload[12:])[:size]

def wait_for_response(connection, session, opcode):
    while True:
        message = connection.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True)
        payload_header = extract_header(message)
        (resp_session, _, _, req_opcode) = parse_header(payload_header)[1:5]
        if resp_session != session:
            #print('Session id is %u instead of %u. Drop' % (resp_session, session))
            continue

        if req_opcode != opcode:
            #print('Response to code %u instead of %u. Drop' % (req_opcode, opcode))
            continue

        break
    return message

def send_ftp_msg(connection, session, opcode, data, wait_resp=False, offset=0, req_opcode=0, burst_complete=0, padding=0):
    global _ftp_seq
    _ftp_seq += 1
    if _ftp_seq > 65535:
        _ftp_seq = 0
    ftp_msg = struct.pack(HDR_Format, _ftp_seq, session, opcode, len(data), req_opcode, burst_complete, padding, offset) + data
    payload = bytearray(ftp_msg)
    plen = len(payload)
    if plen < MAX_Payload + HDR_Len:
        payload.extend(bytearray([0]*((HDR_Len+MAX_Payload)-plen)))
    connection.mav.file_transfer_protocol_send(
        0,
        connection.target_system,
        connection.target_component,
        payload
    )

    if wait_resp:
        return wait_for_response(connection, session, opcode)

def parse_error(message):
    payload_header = extract_header(message)
    (opcode, size) = parse_header(payload_header)[2:4]
    if opcode != OP_Nack:
        return 'There is no errors'

    data = extract_data(message, size)
    if (size == 0):
        return 'Unknown error'

    err_mes = 'Error: '
    err_code = data[0]
    if err_code == ERR_FailErrno:
        if size < 2:
            return err_mes + 'code not provided'
        else:
            return err_mes + 'code %d' % data[1]
    else:
        return err_mes + {
            ERR_None: 'None',
            ERR_Fail: 'Fail',
            ERR_InvalidDataSize: 'Invalid data size',
            ERR_InvalidSession: 'Invalid session',
            ERR_NoSessionsAvailable: 'No sessions available',
            ERR_EndOfFile: 'End of file',
            ERR_UnknownCommand: 'Unknown command',
            ERR_FileExists: 'File exists',
            ERR_FileProtected: 'File protected',
            ERR_FileNotFound: 'File not found'
        }[err_code]

def check_crc(connection, local_file, remote_file):
    print('Calculating checksum...')
    response = send_ftp_msg(
        connection,
        session = 3,
        opcode = OP_CalcFileCRC32,
        data = bytearray(remote_file, 'ascii'),
        wait_resp = True
    )
    payload_header = extract_header(response)
    (opcode, size) = parse_header(payload_header)[2:4]
    if opcode == OP_Nack:
        print('Failed to calculate CRC32')
        print(parse_error(response))
        return None

    data = extract_data(response, size)
    (remote_crc,) = struct.unpack("<I", data)
    f = open(local_file, mode='rb')
    try:
        content = f.read()
    finally:
        f.close()
    local_crc = Crc32.calc(content)
    print('remote\t\tlocal')
    print('%s\t%s' % (hex(remote_crc)[2:], hex(local_crc)[2:]))
    return (local_crc == remote_crc)