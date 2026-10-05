from abc import ABC, abstractmethod

from stego_cli.io.image import Img


class ImageSteganographyAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def encode(cover: Img, secret: Img) -> Img:
        """Encode a secret image into a cover image."""
        ...

    @staticmethod
    @abstractmethod
    def decode(stego: Img) -> Img:
        """Extract the hidden secret image from a stego image."""
        ...

    @staticmethod
    @abstractmethod
    def desc() -> str:
        """Return a human-readable algorithm description."""
        ...

    @staticmethod
    @abstractmethod
    def capacity(img: Img) -> int:
        """Return the maximum number of secret pixels supported."""
        raise NotImplementedError
