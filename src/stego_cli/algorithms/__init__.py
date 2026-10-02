from types import MappingProxyType as _MPT

from .base import SteganographyAlgorithm
from .lsb import LSBAlgorithm
from .spiral import SpiralAlgorithm

ALGORITHMS: _MPT[str, type[SteganographyAlgorithm]] = _MPT(
    {
        "lsb": LSBAlgorithm,
        "spiral": SpiralAlgorithm,
    }
)
