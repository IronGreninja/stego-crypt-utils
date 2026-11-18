from types import MappingProxyType as _MPT

from .base import SteganographyAlgorithm
from .lsb import LSBAlgorithm
from .lsb332 import LSB332Algorithm
from .spiral import SpiralAlgorithm
from .lsb_indicator import LSBIndicatorAlgorithm

ALGORITHMS: _MPT[str, type[SteganographyAlgorithm]] = _MPT(
    {
        "lsb": LSBAlgorithm,
        "lsb-spiral": SpiralAlgorithm,
        "lsb-332": LSB332Algorithm,
        "lsb-indicator": LSBIndicatorAlgorithm, 
    }
)
