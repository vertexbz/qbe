from __future__ import annotations

from dataclasses import dataclass

from .hadlers import link_handler, blueprint_handler, template_handler
from .src_dst import SrcDst
from ..base import Config
from ...adapter.dataclass import field


@dataclass
class OperationConfig(Config):
    link: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=link_handler, link_target=True, removable=True)
    blueprint: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=blueprint_handler)
    template: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=template_handler, tracked=True, removable=True)

    @classmethod
    def decode(cls, data: dict):
        return cls(
            link=[SrcDst.decode(d) for d in data.get('link', [])],
            blueprint=[SrcDst.decode(d) for d in data.get('blueprint', [])],
            template=[SrcDst.decode(d) for d in data.get('template', [])]
        )
