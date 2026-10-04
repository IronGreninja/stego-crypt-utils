import numpy as np

from stego_cli.io.image import Img

from .base import SteganographyAlgorithm


class LSB332Algorithm(SteganographyAlgorithm):
    @staticmethod
    def encode(message: str, img: Img) -> Img:
        mat = img.imgmatrix()
        data = message.encode()

        height, width, _ = mat.shape
        capacity = height * width  # 1 byte per pixel
        # Store the length in the first 4 bytes
        length_bytes = len(data).to_bytes(4, byteorder="big")
        payload = length_bytes + data
        if len(payload) > capacity:
            raise ValueError(
                f"Message too large: needs {len(payload)} bytes, "
                f"but image has capacity for {capacity} bytes"
            )

        # Pad remaining pixels with zero
        payload += b"\x00" * (capacity - len(payload))

        data_array = np.frombuffer(payload, dtype=np.uint8)

        # Split each byte:
        #
        # 3 bits -> R
        # 3 bits -> G
        # 2 bits -> B
        #
        # R = bits 7-5
        # G = bits 4-2
        # B = bits 1-0

        r_bits = (data_array >> 5) & 0b111
        g_bits = (data_array >> 2) & 0b111
        b_bits = data_array & 0b11

        # Flatten image into pixels
        pixels = mat.reshape(-1, 3)

        # Clear the required LSBs:
        pixels[:, 0] &= 0b11111000
        pixels[:, 1] &= 0b11111000
        pixels[:, 2] &= 0b11111100

        # Insert our data
        pixels[:, 0] |= r_bits
        pixels[:, 1] |= g_bits
        pixels[:, 2] |= b_bits

        return Img.from_matrix(mat)

    @staticmethod
    def decode(img: Img) -> str:
        mat = img.imgmatrix()

        pixels = mat.reshape(-1, 3)

        # Extract:
        # R -> 3 bits
        # G -> 3 bits
        # B -> 2 bits
        r_bits = pixels[:, 0] & 0b111
        g_bits = pixels[:, 1] & 0b111
        b_bits = pixels[:, 2] & 0b11

        # Reconstruct original byte: RRR GGG BB
        data = (
            (r_bits.astype(np.uint8) << 5)
            | (g_bits.astype(np.uint8) << 2)
            | b_bits.astype(np.uint8)
        )

        # First 4 bytes contain message length
        length = int.from_bytes(data[:4].tobytes(), byteorder="big")

        # Extract message
        message_bytes = data[4 : 4 + length].tobytes()

        return message_bytes.decode("utf-8")

    @staticmethod
    def desc() -> str:
        return (
            "Least Significant Bit (LSB) Algorithm using 332 scheme. "
            "Stores 1 byte per pixel. "
            "More storage capacity, but more perceptible."
        )

    @staticmethod
    def capacity(img: Img) -> int:
        w, h, _ = img.imgmatrix().shape
        return w * h - 4
