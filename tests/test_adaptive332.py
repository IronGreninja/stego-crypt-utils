import unittest

import numpy as np

from stego_cli.image_algorithms.adaptive332 import (
    Adaptive332Algorithm,
    choose_embedding_channel,
    embed_adaptive_pixel,
    extract_adaptive_pixel,
    get_indicator,
    select_channel,
    set_indicator,
)
from stego_cli.io.image import Img


class TestAdaptive332PixelOperations(unittest.TestCase):

    def test_green_channel_selection(self):
        cover = np.array([100, 50, 100], dtype=np.uint8)

        self.assertEqual(
            choose_embedding_channel(cover),
            "green",
        )

    def test_blue_channel_selection(self):
        cover = np.array([100, 150, 80], dtype=np.uint8)

        self.assertEqual(
            choose_embedding_channel(cover),
            "blue",
        )

    def test_green_indicator(self):
        red = set_indicator(255, "green")

        self.assertEqual(
            get_indicator(red),
            0b00,
        )

        self.assertEqual(
            select_channel(red),
            "green",
        )

    def test_blue_indicator(self):
        red = set_indicator(255, "blue")

        self.assertEqual(
            get_indicator(red),
            0b01,
        )

        self.assertEqual(
            select_channel(red),
            "blue",
        )

    def test_green_adaptive_embedding(self):
        cover = np.array(
            [100, 50, 100],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        self.assertEqual(
            select_channel(int(stego[0])),
            "green",
        )

    def test_blue_adaptive_embedding(self):
        cover = np.array(
            [100, 150, 80],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        self.assertEqual(
            select_channel(int(stego[0])),
            "blue",
        )

    def test_green_indicator_survives_embedding(self):
        cover = np.array(
            [100, 50, 100],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        self.assertEqual(
            get_indicator(int(stego[0])),
            0b00,
        )

    def test_blue_indicator_survives_embedding(self):
        cover = np.array(
            [100, 150, 80],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        self.assertEqual(
            get_indicator(int(stego[0])),
            0b01,
        )

    def test_green_adaptive_round_trip(self):
        cover = np.array(
            [100, 50, 100],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        recovered = extract_adaptive_pixel(stego)

        expected = np.array(
            [128, 160, 64],
            dtype=np.uint8,
        )

        np.testing.assert_array_equal(
            recovered,
            expected,
        )

    def test_blue_adaptive_round_trip(self):
        cover = np.array(
            [100, 150, 80],
            dtype=np.uint8,
        )

        secret = np.array(
            [255, 175, 95],
            dtype=np.uint8,
        )

        stego = embed_adaptive_pixel(
            cover,
            secret,
        )

        recovered = extract_adaptive_pixel(stego)

        expected = np.array(
            [128, 160, 80],
            dtype=np.uint8,
        )

        np.testing.assert_array_equal(
            recovered,
            expected,
        )


class TestAdaptive332Algorithm(unittest.TestCase):

    def test_capacity(self):
        cover = Img.generate(
            "white",
            (100, 100),
        )

        self.assertEqual(
            Adaptive332Algorithm.capacity(cover),
            10000 - 4,
        )

    def test_encode_decode_image(self):
        cover = Img.generate(
            "white",
            (20, 20),
        )

        secret_matrix = np.array(
            [
                [
                    [255, 175, 95],
                    [128, 64, 32],
                ],
                [
                    [0, 255, 128],
                    [64, 192, 224],
                ],
            ],
            dtype=np.uint8,
        )

        secret = Img.from_matrix(secret_matrix)

        encoded = Adaptive332Algorithm.encode(
            cover=cover,
            secret=secret,
        )

        decoded = Adaptive332Algorithm.decode(
            encoded,
        )

        decoded_matrix = decoded.imgmatrix()

        expected = np.array(
            [
                [
                    [128, 160, 64],
                    [128, 64, 32],
                ],
                [
                    [0, 240, 128],
                    [0, 192, 224],
                ],
            ],
            dtype=np.uint8,
        )

        np.testing.assert_array_equal(
            decoded_matrix,
            expected,
        )

    def test_encode_rejects_oversized_secret(self):
        cover = Img.generate(
            "white",
            (5, 5),
        )

        secret = Img.generate(
            "black",
            (5, 5),
        )

        with self.assertRaises(ValueError):
            Adaptive332Algorithm.encode(
                cover=cover,
                secret=secret,
            )


if __name__ == "__main__":
    unittest.main()
