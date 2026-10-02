from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt
from PIL import Image

RGBImageMatrix = npt.NDArray[np.uint8]


@dataclass
class Img:
    img: Image.Image

    @staticmethod
    def load(path: Path) -> Img:
        image = Image.open(path).convert("RGB")

        return Img(img=image)

    @staticmethod
    def from_matrix(img_matrix: RGBImageMatrix) -> Img:
        return Img(img=Image.fromarray(img_matrix, mode="RGB"))

    def save(self, path: Path) -> None:
        self.img.save(path)

    def imgmatrix(
        self,
    ) -> RGBImageMatrix:
        return np.array(self.img)
