from __future__ import annotations

from typing import Union


# Standard crc16 ccitt, take from msgproto.py in Klipper
def crc16_ccitt(buf: Union[bytes, bytearray]) -> int:
    crc = 0xffff
    for data in buf:
        data ^= crc & 0xff
        data ^= (data & 0x0f) << 4
        crc = ((data << 8) | (crc >> 8)) ^ (data >> 4) ^ (data << 3)
    return crc & 0xFFFF
