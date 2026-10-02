from stego_cli.io.image import Img

from ..base import SteganographyAlgorithm
from .bitops import DELIMITER, bits_to_text, text_to_bits
from .spiral import spiral_coords


class SpiralAlgorithm(SteganographyAlgorithm):
    @staticmethod
    def encode(message: str, img: Img) -> Img:
        out = img.img.copy()  # don't modify the caller's image
        pixels = out.load()
        W, H = out.size
        bit_stream = list(text_to_bits(message))
        capacity = W * H * 3
        if len(bit_stream) > capacity:
            raise ValueError(
                f"Message too long: needs {len(bit_stream)} bits, image holds {capacity}."
            )
        idx = 0
        for (x, y) in spiral_coords(W, H):
            if idx >= len(bit_stream):
                break
            r, g, b = pixels[x, y]
            new_channels = []
            for val in (r, g, b):
                if idx < len(bit_stream):
                    new_channels.append((val & ~1) | int(bit_stream[idx]))
                    idx += 1
                else:
                    new_channels.append(val)
            pixels[x, y] = tuple(new_channels)
        return Img(img=out)

    @staticmethod
    def decode(img: Img) -> str:
        pixels = img.img.load()
        W, H = img.img.size
        bits = []
        delimiter_len = len(DELIMITER)
        for (x, y) in spiral_coords(W, H):
            for val in pixels[x, y]:
                bits.append(str(val & 1))
            if len(bits) >= delimiter_len + 8:
                joined = ''.join(bits)
                if DELIMITER in joined:
                    return bits_to_text(joined)
        raise ValueError("No hidden message found.")

    @staticmethod
    def desc() -> str:
        return (
            "Spiral LSB Algorithm. Stores 1 bit in the LSB of each RGB channel, "
            "walking pixels in a clockwise spiral from the outer edge inward. "
            "Message ends with a delimiter."
        )