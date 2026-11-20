from abc import ABC, abstractmethod

from stego_cli.io.image import Img


class Embedder(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.magic_bytes = b"CCVCS"

    @abstractmethod
    def embed(self, data: str, cover1: Img, cover2: Img) -> tuple[Img, Img]:
        """
        @return (stego_cover1, stego_cover2)
        """

    @abstractmethod
    def extract(self, stego_cover1: Img, stego_cover2: Img) -> str: ...
