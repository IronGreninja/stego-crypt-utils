from types import MappingProxyType as _MPT

from .adaptive332 import Adaptive332Algorithm
from .base import ImageSteganographyAlgorithm

IMAGE_ALGORITHMS: _MPT[str, type[ImageSteganographyAlgorithm]] = _MPT(
    {
        "adaptive-332": Adaptive332Algorithm,
    }
)
