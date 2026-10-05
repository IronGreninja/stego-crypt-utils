import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image
from typer.testing import CliRunner

from stego_cli.cli.app import app


class TestImageCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_image_algo(self):
        result = self.runner.invoke(app, ["image-algo"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("adaptive-332", result.stdout)

    def test_image_capacity(self):
        with TemporaryDirectory() as tmp:
            cover_path = Path(tmp) / "cover.png"

            Image.new("RGB", (20, 20), "white").save(cover_path)

            result = self.runner.invoke(
                app,
                [
                    "image-capacity",
                    "-i",
                    str(cover_path),
                ],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout.strip(), "396")

    def test_image_encode_decode(self):
        with TemporaryDirectory() as tmp:
            cover_path = Path(tmp) / "cover.png"
            secret_path = Path(tmp) / "secret.png"
            stego_path = Path(tmp) / "stego.png"
            recovered_path = Path(tmp) / "recovered.png"

            Image.new(
                "RGB",
                (20, 20),
                "white",
            ).save(cover_path)

            secret_array = np.array(
                [
                    [
                        [255, 0, 0],
                        [0, 255, 0],
                    ],
                    [
                        [0, 0, 255],
                        [255, 255, 255],
                    ],
                ],
                dtype=np.uint8,
            )

            Image.fromarray(
                secret_array,
                mode="RGB",
            ).save(secret_path)

            encode_result = self.runner.invoke(
                app,
                [
                    "image-encode",
                    "-i",
                    str(cover_path),
                    "-s",
                    str(secret_path),
                    "-o",
                    str(stego_path),
                ],
            )

            self.assertEqual(encode_result.exit_code, 0)
            self.assertTrue(stego_path.exists())

            decode_result = self.runner.invoke(
                app,
                [
                    "image-decode",
                    "-i",
                    str(stego_path),
                    "-o",
                    str(recovered_path),
                ],
            )

            self.assertEqual(decode_result.exit_code, 0)
            self.assertTrue(recovered_path.exists())

            recovered = Image.open(recovered_path)

            self.assertEqual(
                recovered.size,
                (2, 2),
            )

            recovered_array = np.array(recovered)

            self.assertEqual(
                recovered_array.shape,
                (2, 2, 3),
            )


if __name__ == "__main__":
    unittest.main()
