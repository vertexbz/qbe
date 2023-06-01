from __future__ import annotations
import os
from qbe.support import services

from .base import BaseTriggerHandler, Trigger
from . import trigger_handler


@trigger_handler('gcode')
class GcodeHandler(BaseTriggerHandler):
    def process(self, trigger: Trigger) -> None:
        if services.klipper is not None:
            tty = os.open(services.klipper.tty, os.O_RDWR)
            os.write(tty, (trigger['gcode'] + '\n').encode('utf-8'))
