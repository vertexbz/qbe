from __future__ import annotations

from dataclasses import fields, MISSING, dataclass
import json
from typing import Union, get_type_hints, Type
from typing_extensions import Unpack

from click import command
from dc_schema import _GetSchema, SchemaAnnotation

from ...adapter.dataclass import field
from ...adapter.yaml import PkgTag
from ...manifest import Manifest
from ...manifest.data_source import ManifestDataSource, get_data_source_types
from ...manifest.triggers import ManifestTrigger
from ...provider.operation import SrcDst, LinkConfig
from ...trigger import get_trigger_types
from ...trigger.base import Trigger


class WrappedSrcDst(SrcDst):
    pass


class GetSchema(_GetSchema):

    @staticmethod
    def wrap_trigger(trigger: Type[Trigger]):
        @dataclass(frozen=True)
        class WrappedTrigger(trigger):
            only: dict = field(default_factory=dict, omitempty=True)
            unless: dict = field(default_factory=dict, omitempty=True)

        WrappedTrigger.__name__ = trigger.__name__
        return WrappedTrigger

    def create_dc_schema(self, dc):
        if hasattr(dc, "SchemaConfig"):
            annotation = getattr(dc.SchemaConfig, "annotation", SchemaAnnotation())
        else:
            annotation = SchemaAnnotation()
        schema = {
            "type": "object",
            "title": dc.__name__,
            **annotation.schema(),
            "properties": {},
            "required": [],
        }
        type_hints = get_type_hints(dc, include_extras=True)
        for f in fields(dc):
            type_ = type_hints[f.name]
            name = f.metadata.get('alias', f.name)
            schema["properties"][name] = self.get_field_schema(
                type_, f.default, SchemaAnnotation()
            )
            field_is_optional = (
                f.default is not MISSING or
                f.default_factory is not MISSING or
                f.metadata.get('omitempty', False)
            )
            if not field_is_optional:
                schema["required"].append(name)
        if not schema["required"]:
            schema.pop("required")
        return schema

    def get_field_schema(self, type_, default, annotation):
        if type_ == Union[str, PkgTag]:
            type_ = str

        if type_ == SrcDst:
            type_ = Union[WrappedSrcDst, tuple[str, str], str]
        if type_ == WrappedSrcDst:
            type_ = SrcDst

        if type_ == LinkConfig:
            type_ = list[SrcDst]

        if type_ == ManifestTrigger:
            type_ = Union[Unpack[[self.wrap_trigger(t) for t in get_trigger_types()]]]

        if type_ == ManifestDataSource:
            type_ = Union[Unpack[get_data_source_types()]]

        return super().get_field_schema(type_, default, annotation)


@command(short_help='Renders manifest json schema')
def manifest_schema():
    print(json.dumps(GetSchema()(Manifest), indent=2, sort_keys=False))
