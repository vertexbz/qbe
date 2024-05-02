from __future__ import annotations

from typing import Iterable

from .entry import Entry
from ...adapter.dataclass import CustomEncode, encode


class ProviderProvided(CustomEncode):
    def __init__(self) -> None:
        self._store: set[Entry] = set()
        self._current: set[Entry] = set()

    @property
    def all(self) -> set[Entry]:
        return self._store

    @property
    def untouched(self) -> set[Entry]:
        return self._store.difference(self._current)

    def custom_encode(self):
        return list(map(encode, self._store))

    def notice(self, path: tuple[str, ...], input=None, output=None, **kw) -> None:
        entry = Entry(path=path, input=input, output=output, metadata=kw)
        self._store.add(entry)
        self._current.add(entry)

    def forget(self, entry: Entry) -> None:
        self._store.remove(entry)
        try:
            self._current.remove(entry)
        except KeyError:
            pass

    @classmethod
    def decode(cls, data: Iterable[dict]) -> ProviderProvided:
        result = cls()

        for item in data:
            result._store.add(Entry.decode(item))

        return result

