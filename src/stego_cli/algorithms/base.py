from abc import ABC, abstractmethod
from pathlib import Path

from stego_cli.io.image import Img


class SteganographyAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def encode(message: str, img: Img) -> Img: ...

    @staticmethod
    @abstractmethod
    def decode(img: Img) -> str: ...

    @staticmethod
    @abstractmethod
    def desc() -> str: ...
