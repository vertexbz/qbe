from __future__ import annotations

from typing import Any

from ...adapter.dataclass import CustomEncode, encode


class Entry(CustomEncode):
    def __init__(self, **kw):
        self._path: tuple[str] = kw.get('path')
        self._input: Any = kw.get('input')
        self._output: Any = kw.get('output')
        self._metadata: dict = kw.get('metadata', {})

    @property
    def path(self) -> tuple[str]:
        return self._path

    @property
    def input(self) -> Any:
        return self._input

    @property
    def output(self) -> Any:
        return self._output

    @property
    def metadata(self) -> dict:
        return self._metadata

    def __eq__(self, other):
        if isinstance(other, Entry):
            return (self._path, self._input, self._output) == (other._path, other._input, other._output)
        return False

    def __hash__(self):
        return hash((Entry, self._path, self._input, self._output))

    def custom_encode(self):
        return {
            'path': encode(self._path),
            'input': encode(self._input),
            'output': encode(self._output),
            'metadata': encode(self._metadata),
        }

    @classmethod
    def decode(cls, data: dict) -> Entry:
        path = data.pop('path')
        if isinstance(path, list):
            path = tuple(path)

        input = data.pop('input')
        if isinstance(input, list):
            input = tuple(input)

        output = data.pop('output')
        if isinstance(output, list):
            output = tuple(output)

        return cls(**data, path=path, input=input, output=output)
