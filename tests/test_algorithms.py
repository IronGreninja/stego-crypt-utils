import unittest

from stego_cli.algorithms import ALGORITHMS
from stego_cli.io.image import Img


class TestAlgorithms(unittest.TestCase):
    def test_encode_decode(self):
        message = "Hello, world!"

        for name, algo in ALGORITHMS.items():
            with self.subTest(algorithm=name):
                image = Img.generate("DarkOliveGreen", (100, 100))

                encoded = algo.encode(message=message, img=image)
                decoded = algo.decode(encoded)

                self.assertEqual(
                    decoded,
                    message,
                    f"{name} failed to decode the original message",
                )


if __name__ == "__main__":
    unittest.main()
