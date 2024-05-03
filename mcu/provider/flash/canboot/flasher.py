from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import struct
from typing import Callable

from .crc import crc16_ccitt
from .node import CanNode

# Katapult Defs
CMD_HEADER = b'\x01\x88'
CMD_TRAILER = b'\x99\x03'
BOOTLOADER_CMDS = {
    'CONNECT': 0x11,
    'SEND_BLOCK': 0x12,
    'SEND_EOF': 0x13,
    'REQUEST_BLOCK': 0x14,
    'COMPLETE': 0x15,
    'GET_CANBUS_ID': 0x16,
}

ACK_SUCCESS = 0xa0
NACK = 0xf1


class CanFlasher:
    def __init__(self, node: CanNode, fw_file: str, stdout_callback: Callable[[str], None]) -> None:
        self.node = node
        self.fw_name = fw_file
        self.fw_sha = hashlib.sha1()
        self.file_size = 0
        self.block_size = 64
        self.block_count = 0
        self.app_start_addr = 0
        self._stdout_callback = stdout_callback

    async def connect_btl(self):
        self._stdout_callback("Attempting to connect to bootloader")
        ret = await self.send_command('CONNECT')
        pinfo = ret[:12]
        mcu_type = ret[12:]
        ver_bytes, start_addr, self.block_size = struct.unpack("<4sII", pinfo)
        self.app_start_addr = start_addr
        proto_version = ".".join([str(v) for v in reversed(ver_bytes[:3])])
        if self.block_size not in [64, 128, 256, 512]:
            raise ConnectionError("Invalid Block Size: %d" % (self.block_size,))
        while mcu_type and mcu_type[-1] == 0x00:
            mcu_type = mcu_type[:-1]
        mcu_type = mcu_type.decode()

        self._stdout_callback(f"Katapult Connected\nProtocol Version: {proto_version}")
        self._stdout_callback(f"Block Size: {self.block_size} bytes")
        self._stdout_callback(f"Application Start: 0x{self.app_start_addr:4X}")
        self._stdout_callback(f"MCU type: {mcu_type}")

    async def verify_canbus_uuid(self, uuid):
        self._stdout_callback("Verifying canbus connection")
        ret = await self.send_command('GET_CANBUS_ID')
        mcu_uuid = sum([v << ((5 - i) * 8) for i, v in enumerate(ret[:6])])
        if mcu_uuid != uuid:
            raise ConnectionError("UUID mismatch (%s vs %s)" % (uuid, mcu_uuid))

    async def send_command(self, cmdname: str, payload: bytes = b"", tries: int = 5) -> bytearray:
        word_cnt = (len(payload) // 4) & 0xFF
        cmd = BOOTLOADER_CMDS[cmdname]
        out_cmd = bytearray(CMD_HEADER)
        out_cmd.append(cmd)
        out_cmd.append(word_cnt)
        if payload:
            out_cmd.extend(payload)
        crc = crc16_ccitt(out_cmd[2:])
        out_cmd.extend(struct.pack("<H", crc))
        out_cmd.extend(CMD_TRAILER)
        last_err = Exception()
        while tries:
            data = bytearray()
            recd_len = 0
            try:
                self.node.write(out_cmd)
                read_done = False
                while not read_done:
                    ret = await self.node.readuntil()
                    data.extend(ret)
                    while len(data) > 7:
                        if data[:2] != CMD_HEADER:
                            data = data[1:]
                            continue
                        recd_len = data[3] * 4
                        read_done = len(data) == recd_len + 8
                        break
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError:
                # logging.info(
                #     f"Response for command {cmdname} timed out, "
                #     f"{tries - 1} tries remaining"
                # )
                pass
            except Exception as e:
                if type(e) is type(last_err) and e.args == last_err.args:
                    last_err = e
                    logging.exception("Can Read Error")
            else:
                trailer = data[-2:]
                recd_crc, = struct.unpack("<H", data[-4:-2])
                calc_crc = crc16_ccitt(data[2:-4])
                recd_ack = data[2]
                cmd_response = 0
                if recd_len:
                    cmd_response, = struct.unpack("<I", data[4:8])
                if trailer != CMD_TRAILER:
                    # logging.info(
                    #     f"Command '{cmdname}': Invalid Trailer Received "
                    #     f"0x{trailer.hex()}"
                    # )
                    pass
                elif recd_crc != calc_crc:
                    # logging.info(
                    #     f"Command '{cmdname}': Frame CRC Mismatch, expected: "
                    #     f"{calc_crc}, received {recd_crc}"
                    # )
                    pass
                elif recd_ack != ACK_SUCCESS:
                    # logging.info(f"Command '{cmdname}': Received NACK")
                    pass
                elif cmd_response != cmd:
                    # logging.info(
                    #     f"Command '{cmdname}': Acknowledged wrong command, "
                    #     f"expected: {cmd:2x}, received: {cmd_response:2x}"
                    # )
                    pass
                else:
                    # Validation passed, return payload sans command
                    if recd_len <= 4:
                        return bytearray()
                    return data[8:recd_len + 4]
            tries -= 1
            # clear the read buffer
            try:
                await self.node.read(1024, timeout=.1)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(.1)
        raise ConnectionError(f"Error sending command [{cmdname}] to Can Device")

    async def send_file(self):
        self._stdout_callback(f"Flashing '{self.fw_name}'...")
        last_percent = 0
        with open(self.fw_name, 'rb') as f:
            f.seek(0, os.SEEK_END)
            self.file_size = f.tell()
            f.seek(0)
            flash_address = self.app_start_addr
            while True:
                buf = f.read(self.block_size)
                if not buf:
                    break

                if len(buf) < self.block_size:
                    buf += b"\xFF" * (self.block_size - len(buf))
                self.fw_sha.update(buf)
                prefix = struct.pack("<I", flash_address)
                for _ in range(3):
                    resp = await self.send_command('SEND_BLOCK', prefix + buf)
                    recd_addr, = struct.unpack("<I", resp)
                    if recd_addr == flash_address:
                        break
                    await asyncio.sleep(.1)
                else:
                    raise ConnectionError(f"Flash write failed, block address 0x{recd_addr:4X}")
                flash_address += self.block_size
                self.block_count += 1

                pct = int((self.block_count * self.block_size) / float(self.file_size) * 100 + .5)
                if pct // 10 != last_percent // 10:
                    self._stdout_callback(f'Block {self.block_count} ({pct}%)...')
                    last_percent = pct

            await self.send_command('SEND_EOF')
            self._stdout_callback(f'Flashing complete!')

    async def verify_file(self):
        self._stdout_callback(f'Verifying uploaded firmware...')
        ver_sha = hashlib.sha1()
        last_percent = 0
        for i in range(self.block_count):
            flash_address = i * self.block_size + self.app_start_addr
            for _ in range(3):
                payload = struct.pack("<I", flash_address)
                resp = await self.send_command("REQUEST_BLOCK", payload)
                recd_addr, = struct.unpack("<I", resp[:4])
                if recd_addr == flash_address:
                    break
                await asyncio.sleep(.1)
            else:
                raise ConnectionError(f"Block Request Error, block: {i}")
            ver_sha.update(resp[4:])

            pct = int((i + 1) / float(self.block_count) * 100)
            if pct // 10 != last_percent // 10:
                self._stdout_callback(f'Block {i + 1}/{self.block_count} ({pct}%)...')
                last_percent = pct

        ver_hex = ver_sha.hexdigest().upper()
        fw_hex = self.fw_sha.hexdigest().upper()
        if ver_hex != fw_hex:
            raise ConnectionError(f"Checksum mismatch: Expected {fw_hex}, Received {ver_hex}")
        self._stdout_callback(f'Verification complete!')

    async def finish(self):
        await self.send_command("COMPLETE")
