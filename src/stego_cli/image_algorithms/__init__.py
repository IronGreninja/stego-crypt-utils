from .adaptive332 import Adaptive332Algorithm
from .base import ImageSteganographyAlgorithm

IMAGE_ALGORITHMS = {
    "adaptive-332": Adaptive332Algorithm,
}

__all__ = [
    "ImageSteganographyAlgorithm",
    "Adaptive332Algorithm",
    "IMAGE_ALGORITHMS",
]
