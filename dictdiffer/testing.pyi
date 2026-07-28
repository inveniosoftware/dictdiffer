# SPDX-FileCopyrightText: 2026 HeeJae Chang.
# SPDX-License-Identifier: MIT

from typing import Hashable, Iterable, List, Optional, Union

from . import diff as diff
from .utils import PathLimit

def assert_no_diff(
    first: object,
    second: object,
    node: Optional[List[object]] = ...,
    ignore: Optional[Iterable[object]] = ...,
    path_limit: Optional[Union[PathLimit, Iterable[Iterable[Hashable]]]] = ...,
    expand: bool = ...,
    tolerance: Optional[float] = ...,
    absolute_tolerance: Optional[float] = ...,
    dot_notation: bool = ...,
) -> None: ...
