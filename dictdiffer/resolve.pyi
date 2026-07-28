# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import Callable, Generic, List, Mapping, Sequence, TypeVar, overload

from typing_extensions import Literal, TypeAlias

from . import _Diff, _PathTuple
from .conflict import Conflict
from .utils import get_path as get_path

_InfoT = TypeVar("_InfoT")
_ResolutionAction: TypeAlias = Callable[
    [Conflict, List[_Diff], List[_Diff], _InfoT],
    bool,
]

class UnresolvedConflictsException(Exception):
    message: str
    content: List[Conflict]
    def __init__(self, unresolved_conflicts: List[Conflict]) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class NoFurtherResolutionException(Exception): ...

class Resolver(Generic[_InfoT]):
    actions: Mapping[_PathTuple, _ResolutionAction[_InfoT]]
    additional_info: _InfoT
    unresolved_conflicts: List[Conflict]

    @overload
    def __init__(
        self: Resolver[None],
        actions: Mapping[_PathTuple, _ResolutionAction[None]],
        additional_info: None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        actions: Mapping[_PathTuple, _ResolutionAction[_InfoT]],
        additional_info: _InfoT,
    ) -> None: ...
    def resolve_conflicts(
        self,
        first_patches: List[_Diff],
        second_patches: List[_Diff],
        conflicts: Sequence[Conflict],
    ) -> None: ...
    def manual_resolve_conflicts(
        self,
        picks: Sequence[Literal["f", "s"]],
    ) -> None: ...
