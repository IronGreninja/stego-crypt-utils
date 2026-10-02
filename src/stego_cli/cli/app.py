import sys
from pathlib import Path
from typing import Annotated

import typer as T

from stego_cli.algorithms import ALGORITHMS
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
