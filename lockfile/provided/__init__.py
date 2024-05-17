from __future__ import annotations

from typing import TYPE_CHECKING

from .provider_provided import ProviderProvided
from ...adapter.dataclass import CustomEncode, encode

if TYPE_CHECKING:
    from ...provider.base import Provider


class Provided(CustomEncode):
    def __init__(self) -> None:
        self._data = {}

    def custom_encode(self) -> dict:
        data = {k: encode(v) for k, v in self._data.items()}
        return {k: v for k, v in data.items() if v}

    def by(self, provider: Provider) -> ProviderProvided:
        if provider.DISCRIMINATOR not in self._data:
            entry = ProviderProvided()
            self._data[provider.DISCRIMINATOR] = entry
            return entry

        return self._data[provider.DISCRIMINATOR]

    def has(self, provider: Provider) -> bool:
        return provider.DISCRIMINATOR in self._data

    @classmethod
    def decode(cls, data: dict):
        result = cls()

        for k, v in data.items():
            result._data[k] = ProviderProvided.decode(v)

        return result
