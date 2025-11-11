from dataclasses import dataclass
from typing import Any, Iterable, Optional

def immutable(wrapped_class: Any) -> Any:
    """
    A decorator that makes a class immutable and hashable by automatically generating boilerplate methods.
    It provides data integrity, hashable records and thread-safety in concurrent contexts for a class.
    """
    return dataclass(frozen=True)(wrapped_class)

# A type that defines sequences of numeric values corresponding to each input price point.
IndicatorRepresentable = Iterable[Optional[float]]
