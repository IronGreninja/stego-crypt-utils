from abc import ABC, abstractmethod

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

    @staticmethod
    @abstractmethod
    def capacity(img: Img) -> int:
        """Approximate Maximum size of message in bytes that can be encoded"""
        raise NotImplementedError
