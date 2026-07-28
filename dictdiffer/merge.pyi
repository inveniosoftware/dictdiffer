# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import (
    Generic,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    overload,
)

from typing_extensions import Literal

from . import _Diff, _PathTuple
from . import diff as diff
from .conflict import Conflict
from .conflict import ConflictFinder as ConflictFinder
from .resolve import Resolver as Resolver
from .resolve import UnresolvedConflictsException as UnresolvedConflictsException
from .resolve import _ResolutionAction
from .unify import Unifier as Unifier
from .utils import PathLimit as PathLimit

_DataT = TypeVar("_DataT")
_InfoT = TypeVar("_InfoT")
_ConstructorDataT = TypeVar("_ConstructorDataT")
_ConstructorInfoT = TypeVar("_ConstructorInfoT")

class Merger(Generic[_DataT, _InfoT]):
    lca: _DataT
    first: _DataT
    second: _DataT
    path_limit: PathLimit
    ignore: Optional[Iterable[object]]
    actions: Mapping[_PathTuple, _ResolutionAction[_InfoT]]
    additional_info: _InfoT
    conflict_finder: ConflictFinder
    resolver: Resolver[_InfoT]
    unifier: Unifier
    conflicts: List[Conflict]
    unresolved_conflicts: List[Conflict]
    first_patches: List[_Diff]
    second_patches: List[_Diff]
    unified_patches: List[_Diff]

    @overload
    def __init__(
        self: Merger[_ConstructorDataT, None],
        lca: _ConstructorDataT,
        first: _ConstructorDataT,
        second: _ConstructorDataT,
        actions: Mapping[_PathTuple, _ResolutionAction[None]],
        path_limits: Iterable[Iterable[Hashable]] = ...,
        additional_info: None = ...,
        ignore: Optional[Iterable[object]] = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: Merger[_ConstructorDataT, _ConstructorInfoT],
        lca: _ConstructorDataT,
        first: _ConstructorDataT,
        second: _ConstructorDataT,
        actions: Mapping[_PathTuple, _ResolutionAction[_ConstructorInfoT]],
        path_limits: Iterable[Iterable[Hashable]] = ...,
        additional_info: _ConstructorInfoT = ...,
        ignore: Optional[Iterable[object]] = ...,
    ) -> None: ...
    def run(self) -> None: ...
    def continue_run(self, picks: Sequence[Literal["f", "s"]]) -> None: ...
    def extract_patches(self) -> None: ...
    def find_conflicts(self) -> None: ...
    def resolve_conflicts(self) -> None: ...
    def unify_patches(self) -> None: ...
