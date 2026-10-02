## Usage

### Setup

```bash
uv sync
uv run stego-cli algo
```

`algo` lists the available algorithms (`lsb`, `spiral`).

### Encoding

```bash
echo "text that you want to hide" | uv run stego-cli encode -a spiral -m - -i "<input image path>" -o "<stego image path>.png"
```

| Option | Description |
|--------|-------------|
| `-a`, `--algo` | Algorithm to use (`lsb` default, or `spiral`) |
| `-m`, `--message` | Path of a text file containing the message, or `-` to read from stdin |
| `-i`, `--input-img` | Path of the cover image |
| `-o`, `--output-img` | Path of the output image (default: `out.png` in the current directory) |

> **Note:** Always save the output as **PNG**. Lossy formats such as JPEG destroy the hidden data.

> **Windows `cmd` users:** don't wrap the message in quotes, since `cmd` would include them in the text. Use `echo text that you want to hide| uv run ...`. In PowerShell, use `"text" | uv run ...`.

### Decoding

```bash
uv run stego-cli decode -a spiral -i "<stego image path>"
```

Use the same `-a` algorithm that was used for encoding.

### Running unit tests

```bash
uv run python -m unittest discover -s tests
```