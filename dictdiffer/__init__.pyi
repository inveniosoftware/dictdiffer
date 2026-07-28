# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import (
    Hashable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import Literal, TypeAlias

_DiffPath: TypeAlias = Union[str, List[object]]
_DiffPair: TypeAlias = Tuple[object, object]
_AddDiff: TypeAlias = Tuple[Literal["add"], _DiffPath, List[_DiffPair]]
_RemoveDiff: TypeAlias = Tuple[Literal["remove"], _DiffPath, List[_DiffPair]]
_ChangeDiff: TypeAlias = Tuple[Literal["change"], _DiffPath, _DiffPair]
_Diff: TypeAlias = Union[_AddDiff, _RemoveDiff, _ChangeDiff]
_PathTuple: TypeAlias = Tuple[Hashable, ...]

_DestinationT = TypeVar("_DestinationT")

from . import utils as utils
from . import version as version
from .utils import EPSILON, PathLimit, are_different
from .utils import dot_lookup as dot_lookup
from .version import __version__ as __version__

ADD: Literal["add"]
REMOVE: Literal["remove"]
CHANGE: Literal["change"]
DICT_TYPES: Tuple[Type[object], ...]
LIST_TYPES: Tuple[Type[object], ...]
SET_TYPES: Tuple[Type[object], ...]
HAS_NUMPY: bool
__all__ = ("diff", "patch", "swap", "revert", "dot_lookup", "__version__")

def diff(
    first: object,
    second: object,
    node: Optional[List[object]] = ...,
    ignore: Optional[Iterable[object]] = ...,
    path_limit: Optional[Union[PathLimit, Iterable[Iterable[Hashable]]]] = ...,
    expand: bool = ...,
    tolerance: Optional[float] = ...,
    absolute_tolerance: Optional[float] = ...,
    dot_notation: bool = ...,
) -> Iterator[_Diff]: ...
def patch(
    diff_result: Iterable[_Diff],
    destination: _DestinationT,
    in_place: bool = ...,
) -> _DestinationT: ...
def swap(diff_result: Iterable[_Diff]) -> Iterator[_Diff]: ...
def revert(
    diff_result: Iterable[_Diff],
    destination: _DestinationT,
    in_place: bool = ...,
) -> _DestinationT: ...
