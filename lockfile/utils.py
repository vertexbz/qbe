from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..qbefile import QBEFile


def for_qbe_file(file: QBEFile) -> str:
    return os.path.join(os.path.dirname(file.path), '.qbe.lock')
