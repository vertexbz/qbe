from __future__ import annotations

from dataclasses import dataclass

from .hadlers import link_handler
from .src_dst import SrcDst
from ..base import Config
from ...adapter.dataclass import field, CustomEncode, encode


@dataclass
class LinkConfig(Config, CustomEncode):
    link: list[SrcDst] = field(default_factory=list, omitempty=True, operation_handler=link_handler, link_target=True, removable=True)

    @classmethod
    def decode(cls, data: list):
        return cls(
            link=[SrcDst.decode(d) for d in data]
        )

    def custom_encode(self):
        return encode(self.link)
