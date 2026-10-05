import numpy as np

from stego_cli.io.image import Img

from .base import ImageSteganographyAlgorithm


METADATA_PIXELS = 4

# Red-channel 2-bit indicators.
INDICATOR_GREEN = 0b00
INDICATOR_BLUE = 0b01


def select_channel(red_value: int) -> str:
    """Determine whether Green or Blue carries the extra payload bit."""
    indicator = red_value & 0b11

    if indicator == INDICATOR_GREEN:
        return "green"
    elif indicator == INDICATOR_BLUE:
        return "blue"

    # Reserved indicator values currently map to Green.
    return "green"


def set_indicator(red_value: int, channel: str) -> int:
    """Store the Green/Blue selection in the two LSBs of Red."""
    red_value &= 0b11111100

    if channel == "green":
        indicator = INDICATOR_GREEN
    elif channel == "blue":
        indicator = INDICATOR_BLUE
    else:
        raise ValueError("Channel must be 'green' or 'blue'")

    return red_value | indicator


def get_indicator(red_value: int) -> int:
    """Return the 2-bit indicator stored in Red."""
    return red_value & 0b11


def choose_embedding_channel(cover_pixel: np.ndarray) -> str:
    """
    Select the channel that will receive the additional payload bit.

    The channel with the lower intensity is selected.
    """
    green = int(cover_pixel[1])
    blue = int(cover_pixel[2])

    if green <= blue:
        return "green"

    return "blue"


def embed_adaptive_pixel(
    pixel: np.ndarray,
    secret_pixel: np.ndarray,
) -> np.ndarray:
    """
    Embed one secret RGB pixel into one cover RGB pixel.

    Red:
        1 payload bit + 2-bit channel indicator

    Green/Blue:
        Selected channel gets 4 payload bits.
        Other channel gets 3 payload bits.

    Total payload:
        1 + 4 + 3 = 8 bits.
    """
    pixel = pixel.copy()

    channel = choose_embedding_channel(pixel)

    # ---------------------------------------------------------
    # RED
    # ---------------------------------------------------------
    secret_r = int(secret_pixel[0])
    r_payload = (secret_r >> 7) & 0b1

    # Preserve Red bits 7..3, store payload in bit 2,
    # and use bits 1..0 for the channel indicator.
    red = int(pixel[0])
    red = (red & 0b11111000) | (r_payload << 2)
    red = set_indicator(red, channel)

    # ---------------------------------------------------------
    # GREEN / BLUE
    # ---------------------------------------------------------
    secret_g = int(secret_pixel[1])
    secret_b = int(secret_pixel[2])

    if channel == "green":
        # Green receives 4 bits, Blue receives 3 bits.
        g_payload = (secret_g >> 4) & 0b1111
        b_payload = (secret_b >> 5) & 0b111

        green = (int(pixel[1]) & 0b11110000) | g_payload
        blue = (int(pixel[2]) & 0b11111000) | b_payload

    else:
        # Blue receives 4 bits, Green receives 3 bits.
        g_payload = (secret_g >> 5) & 0b111
        b_payload = (secret_b >> 4) & 0b1111

        green = (int(pixel[1]) & 0b11111000) | g_payload
        blue = (int(pixel[2]) & 0b11110000) | b_payload

    return np.array(
        [red, green, blue],
        dtype=np.uint8,
    )


def extract_adaptive_pixel(pixel: np.ndarray) -> np.ndarray:
    """Extract one secret RGB pixel from one adaptive stego pixel."""
    red = int(pixel[0])
    green = int(pixel[1])
    blue = int(pixel[2])

    channel = select_channel(red)

    # Recover the single Red payload bit.
    r_payload = (red >> 2) & 0b1
    recovered_r = r_payload << 7

    if channel == "green":
        # Green contains 4 payload bits.
        # Blue contains 3 payload bits.
        g_payload = green & 0b1111
        b_payload = blue & 0b111

        recovered_g = g_payload << 4
        recovered_b = b_payload << 5

    else:
        # Green contains 3 payload bits.
        # Blue contains 4 payload bits.
        g_payload = green & 0b111
        b_payload = blue & 0b1111

        recovered_g = g_payload << 5
        recovered_b = b_payload << 4

    return np.array(
        [recovered_r, recovered_g, recovered_b],
        dtype=np.uint8,
    )


class Adaptive332Algorithm(ImageSteganographyAlgorithm):
    """Adaptive 3-3-2 image-in-image steganography algorithm."""

    @staticmethod
    def encode(cover: Img, secret: Img) -> Img:
        cover_array = cover.imgmatrix()
        secret_array = secret.imgmatrix()

        cover_height, cover_width, _ = cover_array.shape
        secret_height, secret_width, _ = secret_array.shape

        cover_pixels = cover_height * cover_width
        secret_pixels = secret_height * secret_width

        capacity = cover_pixels - METADATA_PIXELS

        if secret_pixels > capacity:
            raise ValueError(
                f"Secret image is too large. "
                f"Capacity: {capacity} pixels, "
                f"required: {secret_pixels} pixels."
            )

        stego = cover_array.copy()

        # -----------------------------------------------------
        # Store secret dimensions in the first 4 pixels.
        #
        # Each metadata byte is stored as:
        #   3 bits -> R
        #   3 bits -> G
        #   2 bits -> B
        # -----------------------------------------------------
        metadata = [
            (secret_width >> 8) & 0xFF,
            secret_width & 0xFF,
            (secret_height >> 8) & 0xFF,
            secret_height & 0xFF,
        ]

        flat_stego = stego.reshape(-1, 3)

        for i, value in enumerate(metadata):
            flat_stego[i] = np.array(
                [
                    (value >> 5) & 0b111,
                    (value >> 2) & 0b111,
                    value & 0b11,
                ],
                dtype=np.uint8,
            )

        # -----------------------------------------------------
        # Embed secret pixels.
        # -----------------------------------------------------
        flat_secret = secret_array.reshape(-1, 3)

        for i, secret_pixel in enumerate(flat_secret):
            cover_index = i + METADATA_PIXELS

            flat_stego[cover_index] = embed_adaptive_pixel(
                flat_stego[cover_index],
                secret_pixel,
            )

        return Img.from_matrix(stego)

    @staticmethod
    def decode(stego: Img) -> Img:
        stego_array = stego.imgmatrix()
        flat_stego = stego_array.reshape(-1, 3)

        if len(flat_stego) < METADATA_PIXELS:
            raise ValueError("Stego image is too small to contain metadata.")

        # -----------------------------------------------------
        # Recover secret dimensions.
        # -----------------------------------------------------
        metadata = []

        for i in range(METADATA_PIXELS):
            r, g, b = [int(x) for x in flat_stego[i]]

            value = (
                ((r & 0b111) << 5)
                | ((g & 0b111) << 2)
                | (b & 0b11)
            )

            metadata.append(value)

        secret_width = (metadata[0] << 8) | metadata[1]
        secret_height = (metadata[2] << 8) | metadata[3]

        if secret_width <= 0 or secret_height <= 0:
            raise ValueError("Invalid secret image dimensions.")

        required_pixels = secret_width * secret_height
        available_pixels = len(flat_stego) - METADATA_PIXELS

        if required_pixels > available_pixels:
            raise ValueError(
                "Invalid metadata: secret image exceeds stego capacity."
            )

        # -----------------------------------------------------
        # Extract secret pixels.
        # -----------------------------------------------------
        secret_pixels = []

        for i in range(required_pixels):
            cover_index = i + METADATA_PIXELS

            secret_pixel = extract_adaptive_pixel(
                flat_stego[cover_index]
            )

            secret_pixels.append(secret_pixel)

        secret_array = np.array(
            secret_pixels,
            dtype=np.uint8,
        ).reshape(
            secret_height,
            secret_width,
            3,
        )

        return Img.from_matrix(secret_array)

    @staticmethod
    def desc() -> str:
        return (
            "Adaptive 332 image steganography. Uses the two LSBs of "
            "Red as a Green/Blue channel indicator, while distributing "
            "8 payload bits adaptively across RGB channels."
        )

    @staticmethod
    def capacity(img: Img) -> int:
        height, width, _ = img.imgmatrix().shape
        return max(0, height * width - METADATA_PIXELS)
