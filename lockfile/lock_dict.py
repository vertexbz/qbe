from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Callable

from ..adapter.dataclass import encode

if TYPE_CHECKING:
    from . import LockFile

T = TypeVar('T')
K = TypeVar('K')


class LockDict(dict[K, T]):
    def __init__(
        self, lock: LockFile, key_type: Optional[Type[K]] = None,
        value_constructor: Optional[Callable[[K], T]] = None
    ):
        super().__init__()
        self._lock = lock
        self._key_type = key_type
        self._value_constructor = value_constructor

    def _check_key(self, key: K):
        if self._key_type and not isinstance(key, self._key_type):
            raise KeyError(f"Key must be an instance of '{self._key_type}'")

    def __setitem__(self, key: K, value: T):
        self._check_key(key)
        super().__setitem__(key, value)

    def __getitem__(self, key: K) -> Optional[T]:
        self._check_key(key)
        return super().__getitem__(key)

    def __delitem__(self, __key):
        super().__delitem__(__key)

    def always(self, key: K) -> T:
        self._check_key(key)

        if key in self:
            return super().__getitem__(key)

        if not self._value_constructor:
            raise RuntimeError('value_constructor not defined!')

        value = self._value_constructor(key)
        super().__setitem__(key, value)
        return value

    def to_dict(self) -> dict:
        return {str(k): encode(v) for k, v in dict(self).items()}

    def difference(self, other_keys: set[K]) -> dict:
        removed_keys = set(self.keys()).difference(other_keys)
        return {k: v for k, v in self.items() if k in removed_keys}
