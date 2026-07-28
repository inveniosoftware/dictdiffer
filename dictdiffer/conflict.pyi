# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import Iterable, List, Optional

from typing_extensions import Literal

from . import _Diff
from .utils import get_path as get_path
from .utils import is_super_path as is_super_path

class Conflict:
    first_patch: _Diff
    second_patch: _Diff
    take: Optional[Literal["f", "s"]]
    def __init__(self, patch1: _Diff, patch2: _Diff) -> None: ...
    def take_patch(self) -> _Diff: ...
    def __repr__(self) -> str: ...

class ConflictFinder:
    conflicts: List[Conflict]
    def find_conflicts(
        self,
        first_patches: Iterable[_Diff],
        second_patches: Iterable[_Diff],
    ) -> List[Conflict]: ...
