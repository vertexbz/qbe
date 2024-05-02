from __future__ import annotations

from dataclasses import dataclass

from ..adapter.dataclass import field, CustomEncode, encode
from ..optionable import Optionable
from ..trigger import build as build_trigger, Trigger


@dataclass
class ManifestTrigger(Optionable, CustomEncode):
    trigger: Trigger
    only: dict = field(default_factory=dict, omitempty=True)
    unless: dict = field(default_factory=dict, omitempty=True)

    @classmethod
    def decode(cls, data: dict) -> ManifestTrigger:
        return cls(
            trigger=build_trigger(data),
            only=data.get('only', {}),
            unless=data.get('unless', {})
        )

    def custom_encode(self):
        result = encode(self.trigger)
        if self.only:
            result['only'] = self.only
        if self.unless:
            result['unless'] = self.unless
        return result


@dataclass
class ManifestTriggers:
    """Package triggers"""
    installed: list[ManifestTrigger] = field(default_factory=list, omitempty=True)
    updated: list[ManifestTrigger] = field(default_factory=list, omitempty=True)
    removed: list[ManifestTrigger] = field(default_factory=list, omitempty=True)
    always: list[ManifestTrigger] = field(default_factory=list, omitempty=True)

    @classmethod
    def decode(cls, data: dict) -> ManifestTriggers:
        return cls(
            installed=[ManifestTrigger.decode(t) for t in data.get('installed', [])],
            updated=[ManifestTrigger.decode(t) for t in data.get('updated', [])],
            removed=[ManifestTrigger.decode(t) for t in data.get('removed', [])],
            always=[ManifestTrigger.decode(t) for t in data.get('always', [])],
        )

    def collect(self, installed=False, updated=False, removed=False, options: dict = None) -> list[ManifestTrigger]:
        if not options:
            options = {}

        triggers = []
        if installed:
            for trigger in self.installed:
                if trigger.available(options):
                    triggers.append(trigger)

        if updated:
            for trigger in self.updated:
                if trigger.available(options):
                    triggers.append(trigger)

        if removed:
            for trigger in self.removed:
                if trigger.available(options):
                    triggers.append(trigger)

        for trigger in self.always:
            if trigger.available(options):
                triggers.append(trigger)

        return triggers