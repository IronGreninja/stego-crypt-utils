import numpy as np

from stego_cli.io.image import Img

from .base import SteganographyAlgorithm

_HEADER_BITS = 32


def _slot_indices(mat: np.ndarray) -> np.ndarray:
    pixels = mat.reshape(-1, 3)
    n = pixels.shape[0]
    control = pixels[:, 0] & 0b11
    use_g = control >= 2  # 10, 11
    use_b = (control & 1) == 1  # 01, 11
    valid = np.stack([use_g, use_b], axis=1).reshape(-1)

    pixel_idx = np.repeat(np.arange(n), 2)
    channel_idx = np.tile(np.array([1, 2]), n)

    return (pixel_idx * 3 + channel_idx)[valid]


class LSBIndicatorAlgorithm(SteganographyAlgorithm):
    @staticmethod
    def encode(message: str, img: Img) -> Img:
        mat = img.imgmatrix()
        data = message.encode()

        length_bits = np.unpackbits(np.array([len(data)], dtype=">u4").view(np.uint8))
        data_bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        bits = np.concatenate([length_bits, data_bits])

        slots = _slot_indices(mat)
        if len(bits) > len(slots):
            raise ValueError(
                f"Message too large: needs {len(bits)} bits, "
                f"but image has capacity for {len(slots)} bits"
            )

        flat = mat.reshape(-1)
        target = slots[: len(bits)]
        flat[target] = (flat[target] & 0xFE) | bits

        return Img.from_matrix(mat)

    @staticmethod
    def decode(img: Img) -> str:
        mat = img.imgmatrix()
        flat = mat.reshape(-1)

        slots = _slot_indices(mat)
        if len(slots) < _HEADER_BITS:
            raise ValueError("Image does not contain a complete message")

        length_bits = flat[slots[:_HEADER_BITS]] & 1
        length = int.from_bytes(np.packbits(length_bits).tobytes(), byteorder="big")

        end = _HEADER_BITS + length * 8
        if end > len(slots):
            raise ValueError("Image does not contain a complete message")

        data_bits = flat[slots[_HEADER_BITS:end]] & 1
        data = np.packbits(data_bits).tobytes()

        return data.decode("utf-8")

    @staticmethod
    def desc() -> str:
        return (
            "Indicator LSB Algorithm. The 2 low bits of each pixel's Red "
            "channel decide where to hide data: 00 = skip, 01 = Blue, "
            "10 = Green, 11 = Green + Blue. Capacity depends on image content."
        )

    @staticmethod
    def capacity(img: Img) -> int:
        """Exact capacity in bytes (depends on the Red channel's low bits)."""
        slots = len(_slot_indices(img.imgmatrix()))
        return max(0, (slots - _HEADER_BITS) // 8)