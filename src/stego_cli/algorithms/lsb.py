from pathlib import Path

import numpy as np

from stego_cli.io.image import Img

from .base import SteganographyAlgorithm


class LSBAlgorithm(SteganographyAlgorithm):
    @staticmethod
    def encode(message: str, img_path: Path) -> Img:
        im = Img.load(img_path)
        mat = im.imgmatrix()
        data = message.encode()

        # 32-bit message length prefix, in bytes.
        length_bits = np.unpackbits(np.array([len(data)], dtype=">u4").view(np.uint8))

        data_bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

        bits = np.concatenate([length_bits, data_bits])

        capacity = mat.shape[0] * mat.shape[1] * 3
        if len(bits) > capacity:
            raise ValueError(
                f"Message too large: needs {len(bits)} bits, "
                f"but image has capacity for {capacity} bits"
            )

        # Flatten RGB channels and replace their LSBs.
        flat = mat.reshape(-1)
        flat[: len(bits)] = (flat[: len(bits)] & 0xFE) | bits

        return Img.from_matrix(mat)

    @staticmethod
    def decode(img_path: Path) -> str:
        im = Img.load(img_path)
        mat = im.imgmatrix()

        flat = mat.reshape(-1)

        # First 32 bits contain message length in bytes.
        length_bits = flat[:32] & 1
        length_bytes = np.packbits(length_bits).tobytes()
        length = int.from_bytes(length_bytes, byteorder="big")

        data_bits = flat[32 : 32 + length * 8] & 1

        if len(data_bits) < length * 8:
            raise ValueError("Image does not contain a complete message")

        data = np.packbits(data_bits).tobytes()

        return data.decode("utf-8")

    @staticmethod
    def desc() -> str:
        return (
            "Least Significant Bit (LSB) Algorithm. "
            "Stores 1 bit data in each lsb position of each color channel (RGB)"
        )
