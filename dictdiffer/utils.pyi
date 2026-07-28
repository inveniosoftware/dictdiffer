# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import (
    Dict,
    Generic,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Literal, TypeAlias

from . import _Diff, _DiffPair, _DiffPath, _PathTuple

_ValueT = TypeVar("_ValueT")
_SourceT = TypeVar("_SourceT")
_PathPatch: TypeAlias = Tuple[str, _DiffPath, Sequence[_DiffPair]]

num_types: Tuple[Type[int], Type[float]]
EPSILON: float

class WildcardDict(Dict[_PathTuple, _ValueT], Generic[_ValueT]):
    star_keys: Set[_PathTuple]
    plus_keys: Set[_PathTuple]

    @overload
    def __init__(self, values: None = ...) -> None: ...
    @overload
    def __init__(self, values: Mapping[_PathTuple, _ValueT]) -> None: ...
    def __getitem__(self, key: _PathTuple) -> _ValueT: ...
    def __setitem__(self, key: _PathTuple, value: _ValueT) -> None: ...
    def query_path(self, key: _PathTuple) -> _PathTuple: ...

class PathLimit:
    final_key: Hashable
    dict: Dict[Hashable, object]
    def __init__(
        self,
        path_limits: Iterable[Iterable[Hashable]] = ...,
        final_key: Optional[Hashable] = ...,
    ) -> None: ...
    def path_is_limit(self, key_path: Iterable[Hashable]) -> bool: ...

def create_dotted_node(node: Sequence[object]) -> Union[str, List[object]]: ...
def get_path(patch: Union[_Diff, _PathPatch]) -> Tuple[object, ...]: ...
def is_super_path(path1: Iterable[object], path2: Iterable[object]) -> bool: ...
def nested_hash(obj: object) -> Optional[int]: ...

@overload
def dot_lookup(
    source: _SourceT,
    lookup: None,
    parent: bool = ...,
) -> _SourceT: ...
@overload
def dot_lookup(
    source: _SourceT,
    lookup: Literal[""],
    parent: bool = ...,
) -> _SourceT: ...
@overload
def dot_lookup(
    source: object,
    lookup: Union[str, List[object]],
    parent: bool = ...,
) -> object: ...

def are_different(
    first: object,
    second: object,
    tolerance: Optional[float],
    absolute_tolerance: Optional[float] = ...,
) -> bool: ...
