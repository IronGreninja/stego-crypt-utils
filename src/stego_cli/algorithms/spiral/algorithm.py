from stego_cli.io.image import Img

from ..base import SteganographyAlgorithm
from .bitops import DELIMITER_BYTES
from .spiral import spiral_coords


class SpiralAlgorithm(SteganographyAlgorithm):

    @staticmethod
    def encode(message: str, img: Img) -> Img:
        out = img.img.copy()  # don't modify the caller's image
        pixels = out.load()
        W, H = out.size

        payload = message.encode("utf-8") + DELIMITER_BYTES
        capacity = W * H  # 1 byte per pixel
        if len(payload) > capacity:
            raise ValueError(
                f"Message too long: needs {len(payload)} bytes, image holds {capacity}."
            )

        coords = spiral_coords(W, H)
        for byte, (x, y) in zip(payload, coords):
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                (r & 0b11111000) | (byte >> 5),
                (g & 0b11111000) | ((byte >> 2) & 0b111),
                (b & 0b11111100) | (byte & 0b11),
            )
        return Img(img=out)

    @staticmethod
    def decode(img: Img) -> str:
        pixels = img.img.load()
        W, H = img.img.size

        data = bytearray()
        for (x, y) in spiral_coords(W, H):
            r, g, b = pixels[x, y]
            data.append(((r & 0b111) << 5) | ((g & 0b111) << 2) | (b & 0b11))
            if data.endswith(DELIMITER_BYTES):
                return bytes(data[: -len(DELIMITER_BYTES)]).decode("utf-8")
        raise ValueError("No hidden message found.")

    @staticmethod
    def desc() -> str:
        return (
            "Spiral LSB Algorithm (3-3-2). Stores 1 byte per pixel "
            "(3 bits in Red, 3 in Green, 2 in Blue), walking pixels in a "
            "clockwise spiral from the outer edge inward. "
            "Message ends with a delimiter. More capacity, but more perceptible."
        )

    @staticmethod
    def capacity(img: Img) -> int:
        w, h = img.img.size
        return max(0, w * h - len(DELIMITER_BYTES))