from __future__ import annotations

import asyncio
import errno
import logging
import socket
import struct
from typing import Dict, List

from .flasher import CanFlasher
from .node import CanNode

CAN_FMT = "<IB3x8s"


# Klipper Admin Defs (for jumping to bootloader)
KLIPPER_ADMIN_ID = 0x3f0
KLIPPER_SET_NODE_CMD = 0x01
KLIPPER_REBOOT_CMD = 0x02

# CAN Admin Defs
CANBUS_ID_ADMIN = 0x3f0
CANBUS_ID_ADMIN_RESP = 0x3f1
CANBUS_CMD_QUERY_UNASSIGNED = 0x00
CANBUS_CMD_SET_NODEID = 0x11
CANBUS_CMD_CLEAR_NODE_ID = 0x12
CANBUS_RESP_NEED_NODEID = 0x20
CANBUS_NODEID_OFFSET = 128


class CanSocket:
    def __init__(self, loop: asyncio.AbstractEventLoop, interface: str):
        self._loop = loop
        self._interface = interface

        self.cansock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.admin_node = CanNode(CANBUS_ID_ADMIN, self)
        self.nodes: Dict[int, CanNode] = {
            CANBUS_ID_ADMIN_RESP: self.admin_node
        }

        self.input_buffer = b""
        self.output_packets: List[bytes] = []
        self.input_busy = False
        self.output_busy = False
        self.closed = True

    def _handle_can_response(self) -> None:
        try:
            data = self.cansock.recv(4096)
        except socket.error as e:
            # If bad file descriptor allow connection to be
            # closed by the data check
            if e.errno == errno.EBADF:
                logging.exception("Can Socket Read Error, closing")
                data = b''
            else:
                return
        if not data:
            # socket closed
            self._close()
            return
        self.input_buffer += data
        if self.input_busy:
            return
        self.input_busy = True
        while len(self.input_buffer) >= 16:
            packet = self.input_buffer[:16]
            self._process_packet(packet)
            self.input_buffer = self.input_buffer[16:]
        self.input_busy = False

    def _process_packet(self, packet: bytes) -> None:
        can_id, length, data = struct.unpack(CAN_FMT, packet)
        can_id &= socket.CAN_EFF_MASK
        payload = data[:length]
        node = self.nodes.get(can_id)
        if node is not None:
            node.feed_data(payload)

    def send(self, can_id: int, payload: bytes = b"") -> None:
        if can_id > 0x7FF:
            can_id |= socket.CAN_EFF_FLAG
        if not payload:
            packet = struct.pack(CAN_FMT, can_id, 0, b"")
            self.output_packets.append(packet)
        else:
            while payload:
                length = min(len(payload), 8)
                pkt_data = payload[:length]
                payload = payload[length:]
                packet = struct.pack(
                    CAN_FMT, can_id, length, pkt_data)
                self.output_packets.append(packet)
        if self.output_busy:
            return
        self.output_busy = True
        asyncio.create_task(self._do_can_send())

    async def _do_can_send(self):
        while self.output_packets:
            packet = self.output_packets.pop(0)
            try:
                await self._loop.sock_sendall(self.cansock, packet)
            except socket.error:
                logging.info("Socket Write Error, closing")
                self._close()
                break
        self.output_busy = False

    def _set_node_id(self, uuid: int) -> CanNode:
        # Convert ID to a list
        plist = [(uuid >> ((5 - i) * 8)) & 0xFF for i in range(6)]
        plist.insert(0, CANBUS_CMD_SET_NODEID)
        node_id = len(self.nodes) + CANBUS_NODEID_OFFSET
        plist.append(node_id)
        payload = bytes(plist)
        self.admin_node.write(payload)
        decoded_id = node_id * 2 + 0x100
        node = CanNode(decoded_id, self)
        self.nodes[decoded_id + 1] = node
        return node

    def _reset_nodes(self) -> None:
        # output_line("Resetting all bootloader node IDs...")
        payload = bytes([CANBUS_CMD_CLEAR_NODE_ID])
        self.admin_node.write(payload)

    def _close(self) -> None:
        if self.closed:
            return
        self.closed = True
        for node in self.nodes.values():
            node.close()
        self._loop.remove_reader(self.cansock.fileno())
        self.cansock.close()

    def __enter__(self):
        try:
            self.cansock.bind((self._interface,))
        except Exception:
            raise ConnectionError(f"Unable to bind socket to {self._interface}")
        self.closed = False
        self.cansock.setblocking(False)
        self._loop.add_reader(self.cansock.fileno(), self._handle_can_response)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    async def bootloader(self, uuid: int) -> None:
        # TODO: Send Klipper Admin command to jump to bootloader.
        # It will need to be implemented
        # output_line("Sending bootloader jump command...")
        plist = [(uuid >> ((5 - i) * 8)) & 0xFF for i in range(6)]
        plist.insert(0, KLIPPER_REBOOT_CMD)
        self.send(KLIPPER_ADMIN_ID, bytes(plist))
        # output_line("Bootloader request command sent")

    async def flash(self, uuid: int, fw_path: str) -> None:
        # await self.bootloader(uuid)
        await asyncio.sleep(.5)
        self._reset_nodes()
        await asyncio.sleep(1.0)
        node = self._set_node_id(uuid)
        flasher = CanFlasher(node, fw_path)
        await asyncio.sleep(.5)
        try:
            await flasher.connect_btl()
            await flasher.verify_canbus_uuid(uuid)
            await flasher.send_file()
            await flasher.verify_file()
        finally:
            # always attempt to send the complete command. If
            # there is an error it will exit the bootloader
            # unless comms were broken
            await flasher.finish()

    async def query(self):
        self._reset_nodes()
        await asyncio.sleep(.5)

        payload = bytes([CANBUS_CMD_QUERY_UNASSIGNED])
        self.admin_node.write(payload)
        curtime = self._loop.time()
        endtime = curtime + 2.

        results: dict[str, str] = dict()
        while curtime < endtime:
            timeout = max(.1, endtime - curtime)
            try:
                resp = await self.admin_node.read(8, timeout)
            except asyncio.TimeoutError:
                continue
            finally:
                curtime = self._loop.time()
            if len(resp) < 7 or resp[0] != CANBUS_RESP_NEED_NODEID:
                continue

            app_names = {
                KLIPPER_SET_NODE_CMD: "Klipper",
                CANBUS_CMD_SET_NODEID: "Katapult"
            }
            app = "Unknown"
            if len(resp) > 7:
                app = app_names.get(resp[7], "Unknown")

            data = resp[1:7]
            results[data.hex()] = app

        return results
