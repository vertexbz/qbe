from __future__ import annotations

from qbe.utils import jinja

from .base import BaseTriggerHandler, Trigger
from . import trigger_handler


@trigger_handler('message')
class MessageHandler(BaseTriggerHandler):
    def process(self, trigger: Trigger) -> None:
        self.messages.append(jinja.render(trigger['message'], self.context))
