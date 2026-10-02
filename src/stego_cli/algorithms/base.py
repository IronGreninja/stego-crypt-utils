from abc import ABC, abstractmethod
from pathlib import Path

from stego_cli.io.image import Img


class SteganographyAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def encode(message: str, img_path: Path) -> Img: ...

    @staticmethod
    @abstractmethod
    def decode(img_path: Path) -> str: ...

    @staticmethod
    @abstractmethod
    def desc() -> str: ...
