from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import trigger
from .base import Trigger
from ..adapter.jinja import render

if TYPE_CHECKING:
    from ..updatable import Updatable
    from ..updatable.progress import ProgressRoot


@trigger('message')
@dataclass(frozen=True)
class MessageTrigger(Trigger):
    message: str

    @classmethod
    def decode(cls, data: dict):
        return cls(message=data['message'])

    async def handle(self, progress: ProgressRoot, updatable: Updatable):
        progress.log('Message: ' + render(self.message, updatable.template_context()))
