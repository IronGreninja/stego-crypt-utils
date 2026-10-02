from types import MappingProxyType as _MPT

from .base import SteganographyAlgorithm
from .lsb import LSBAlgorithm

ALGORITHMS: _MPT[str, type[SteganographyAlgorithm]] = _MPT(
    {
        "lsb": LSBAlgorithm,
    }
)
