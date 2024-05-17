from __future__ import annotations

from abc import abstractmethod
import copy
import dataclasses
from dataclasses import fields, MISSING, Field, is_dataclass
import enum
import sys
from typing import get_type_hints, get_args, get_origin, Union


class CustomEncode:
    @abstractmethod
    def custom_encode(self):
        raise NotImplementedError('Subclasses must implement')


class UniversalDecoder:
    @classmethod
    def _field_decoder(cls, field: Field, typ: type):
        if get_origin(typ) in (list,):
            typ = get_args(typ)[0]

        if get_origin(typ) in (Union,):
            args = list(filter(lambda t: t is not type(None), get_args(typ)))
            if len(args) == 1:
                typ = args[0]

        if decoder := field.metadata.get('decoder'):
            return decoder

        if (decoder := getattr(typ, 'decode', None)) and callable(decoder):
            return decoder

        if issubclass(typ, enum.Enum):
            return typ

        return None

    @classmethod
    def _field_name(cls, field: Field):
        return field.metadata.get('alias', field.name)

    @classmethod
    def _decode_params(cls, data: dict):
        normalized_data = dict()

        types = get_type_hints(cls)
        for field in fields(cls):
            dict_key = cls._field_name(field)
            if dict_key in data:
                value = data.get(dict_key)

                if decoder := cls._field_decoder(field, types[field.name]):
                    value = decoder(value)

                normalized_data[field.name] = value

        return normalized_data

    @classmethod
    def decode(cls, data: dict):
        return cls(**cls._decode_params(data))  # type: ignore


def field(
    *, default=MISSING, default_factory=MISSING,
    init=True, repr=True, hash=None, compare=True, metadata=None, kw_only=MISSING,
    name=None, omitempty=False, **kw
):
    if kw:
        kw.update(metadata or {})
        metadata = kw
    elif (name or omitempty) and not metadata:
        metadata = dict()

    if name:
        metadata['alias'] = name
    if omitempty:
        metadata['omitempty'] = omitempty

    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    if sys.version_info < (3, 10):
        return Field(default, default_factory, init, repr, hash, compare, metadata)  # type: ignore

    return Field(default, default_factory, init, repr, hash, compare, metadata, kw_only)  # type: ignore


def encode(obj):
    if isinstance(obj, CustomEncode):
        return obj.custom_encode()
    elif is_dataclass(obj):
        result = []
        for f in fields(obj):
            value = encode(getattr(obj, f.name))

            if f.metadata.get('omitempty', False):
                if not value:
                    continue

                if f.default != dataclasses.MISSING and value == f.default:
                    continue

                if f.default_factory != dataclasses.MISSING and value == f.default_factory():
                    continue

            name = f.metadata.get('alias', f.name)
            result.append((name, value))
        return dict(result)
    elif isinstance(obj, (list, tuple, set)):
        return [encode(v) for v in obj]
    elif isinstance(obj, dict):
        return type(obj)((encode(k), encode(v)) for k, v in obj.items())
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        return copy.deepcopy(obj)


__all__ = ['field', 'encode', 'CustomEncode', 'UniversalDecoder']
