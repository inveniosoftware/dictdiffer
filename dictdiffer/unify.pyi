# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import Iterable, List

from . import _Diff
from .conflict import Conflict
from .utils import get_path as get_path
from .utils import nested_hash as nested_hash

class Unifier:
    unified_patches: List[_Diff]
    def unify(
        self,
        first_patches: List[_Diff],
        second_patches: List[_Diff],
        conflicts: Iterable[Conflict],
    ) -> List[_Diff]: ...
