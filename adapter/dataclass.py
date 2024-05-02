from __future__ import annotations

from abc import abstractmethod
import copy
import dataclasses
from dataclasses import fields, MISSING, Field, is_dataclass
import enum
import sys


class CustomEncode:
    @abstractmethod
    def custom_encode(self):
        raise NotImplementedError('Subclasses must implement')


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


__all__ = ['field', 'encode', 'CustomEncode']
