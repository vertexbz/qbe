from __future__ import annotations

from dataclasses import dataclass

from .hadlers import system_link_handler, system_blueprint_handler, system_template_handler
from .src_dst import SrcDst
from ..base import Config
from ...adapter.dataclass import field


@dataclass
class SystemOperationConfig(Config):
    link: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=system_link_handler, link_target=True, removable=True)
    blueprint: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=system_blueprint_handler)
    template: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=system_template_handler, tracked=True, removable=True)

    @classmethod
    def decode(cls, data: dict):
        return cls(
            link=[SrcDst.decode(d) for d in data.get('link', [])],
            blueprint=[SrcDst.decode(d) for d in data.get('blueprint', [])],
            template=[SrcDst.decode(d) for d in data.get('template', [])]
        )
