import sys
from pathlib import Path
from typing import Annotated

import typer as T

from stego_cli.algorithms import ALGORITHMS
from stego_cli.image_algorithms import IMAGE_ALGORITHMS
from stego_cli.io.image import Img

app = T.Typer(no_args_is_help=True)

enc_default_outpath = Path.cwd() / "out.png"


@app.callback()
def root():
    """CLI app to encode/decode text in/out-of an image."""


@app.command()
def encode(
    message_src: Annotated[
        str,
        T.Option(
            "-m",
            "--message",
            help="Path of the file which contains the message. Use '-' to read from stdin",
        ),
    ],
    input_img: Annotated[Path, T.Option("-i", "--input-img")],
    output_img: Annotated[Path, T.Option("-o", "--output-img")] = enc_default_outpath,
    algo: Annotated[str, T.Option("-a", "--algo")] = "lsb",
):
    """Encode text inside an image."""

    if algo not in ALGORITHMS:
        raise ValueError(
            f"Unknown {algo}. Run `algo` subcommand to see available algorithms"
        )

    message: str
    if message_src == "-":
        message = sys.stdin.read().strip()
    else:
        with open(Path(message_src)) as f:
            message = f.read().strip()

    ALGORITHMS[algo].encode(message=message, img=Img.load(input_img)).save(output_img)

    print("Encoding Successful")


@app.command()
def decode(
    input_img: Annotated[Path, T.Option("-i", "--input-img")],
    algo: Annotated[str, T.Option("-a", "--algo")] = "lsb",
):
    """Decode text from an image."""

    message = ALGORITHMS[algo].decode(Img.load(input_img))
    print("Decoding Successful. Extracted message follows:\n")
    print(f"{message}")


@app.command()
def algo():
    """Show informations about available Stego Algorithms."""

    for name, algo in ALGORITHMS.items():
        print(f"{name}: {algo.desc()}")


@app.command()
def capacity(
    input_img: Annotated[Path, T.Option("-i", "--input-img")],
    algo: Annotated[str, T.Option("-a", "--algo")] = "lsb",
):
    """Show how many bytes of data can be encoded."""

    res = ALGORITHMS[algo].capacity(Img.load(input_img))
    print(res)


@app.command("image-encode")
def image_encode(
    input_img: Annotated[
        Path,
        T.Option("-i", "--input-img"),
    ],
    secret_img: Annotated[
        Path,
        T.Option("-s", "--secret-img"),
    ],
    output_img: Annotated[
        Path,
        T.Option("-o", "--output-img"),
    ] = enc_default_outpath,
    algo: Annotated[
        str,
        T.Option("-a", "--algo"),
    ] = "adaptive-332",
):
    """Encode a secret image inside a cover image."""

    if algo not in IMAGE_ALGORITHMS:
        raise ValueError(
            f"Unknown image algorithm: {algo}. "
            "Run `image-algo` to see available image algorithms."
        )

    cover = Img.load(input_img)
    secret = Img.load(secret_img)

    IMAGE_ALGORITHMS[algo].encode(
        cover=cover,
        secret=secret,
    ).save(output_img)

    print("Image encoding successful")


@app.command("image-decode")
def image_decode(
    input_img: Annotated[
        Path,
        T.Option("-i", "--input-img"),
    ],
    output_img: Annotated[
        Path,
        T.Option("-o", "--output-img"),
    ],
    algo: Annotated[
        str,
        T.Option("-a", "--algo"),
    ] = "adaptive-332",
):
    """Extract a hidden image from a stego image."""

    if algo not in IMAGE_ALGORITHMS:
        raise ValueError(
            f"Unknown image algorithm: {algo}. "
            "Run `image-algo` to see available image algorithms."
        )

    IMAGE_ALGORITHMS[algo].decode(
        Img.load(input_img),
    ).save(output_img)

    print("Image decoding successful")


@app.command("image-algo")
def image_algo():
    """Show available image steganography algorithms."""

    for name, algo in IMAGE_ALGORITHMS.items():
        print(f"{name}: {algo.desc()}")


@app.command("image-capacity")
def image_capacity(
    input_img: Annotated[
        Path,
        T.Option("-i", "--input-img"),
    ],
    algo: Annotated[
        str,
        T.Option("-a", "--algo"),
    ] = "adaptive-332",
):
    """Show the maximum number of secret pixels that can be embedded."""

    if algo not in IMAGE_ALGORITHMS:
        raise ValueError(
            f"Unknown image algorithm: {algo}. "
            "Run `image-algo` to see available image algorithms."
        )

    res = IMAGE_ALGORITHMS[algo].capacity(
        Img.load(input_img),
    )

    print(res)
