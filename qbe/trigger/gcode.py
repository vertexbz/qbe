from __future__ import annotations
from qbe.support import services

from .base import BaseTriggerHandler, Trigger
from . import trigger_handler


@trigger_handler('gcode')
class GcodeHandler(BaseTriggerHandler):
    def process(self, trigger: Trigger) -> None:
        if services.klipper is not None:
            services.klipper.gcode(trigger['gcode'])
