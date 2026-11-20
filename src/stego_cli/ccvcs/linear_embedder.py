from hashlib import sha224

import numpy as np

from stego_cli.io.image import Img

from .chunk_manager import Chunk
from .embedder import Embedder
from .erasure_coding import generate_redundant_chunks, recover_original_chunks
from .xor_shares import combine_2_shares, split_2_shares


class LinearEmbedder(Embedder):
    def __init__(self, hmac_key: bytes, chunk_payload_size: int = 100) -> None:
        super().__init__()

        self.chunk_payload_size = chunk_payload_size

        magic_size = len(self.magic_bytes)
        # Header format:
        # >  = Big-endian byte order
        # Xs = X-byte magic number
        # B  = 1-byte unsigned integer (share ID)
        # B  = 1-byte unsigned integer (chunk index)
        self.header_format = f">{magic_size}sBB"

        self.hmac_key = hmac_key

        self.Chunk = Chunk(self.header_format, self.chunk_payload_size, "")

    def embed(self, data: str, cover1: Img, cover2: Img) -> tuple[Img, Img]:
        required_chunks = self.Chunk.calculate_required_chunks(len(data))
        k = required_chunks
        redundancy = k // 2
        m = k + redundancy

        try:
            self._validate_image_capacity(len(data), redundancy, cover1.pixelcount())
        except ValueError as e:
            raise ValueError(f"cover1 size error\n{str(e)}")
        try:
            self._validate_image_capacity(len(data), redundancy, cover2.pixelcount())
        except ValueError as e:
            raise ValueError(f"cover2 size error\n{str(e)}")

        share1, share2 = split_2_shares(data)

        share1_chunks_payloads = self.Chunk.split_payload(share1)
        share2_chunks_payloads = self.Chunk.split_payload(share2)

        share1_chunks_payloads = generate_redundant_chunks(share1_chunks_payloads)
        share2_chunks_payloads = generate_redundant_chunks(share2_chunks_payloads)

        share1_chunks_contents = [
            ((self.magic_bytes, 1, id), payload, ())
            for id, payload in enumerate(share1_chunks_payloads)
        ]
        share2_chunks_contents = [
            ((self.magic_bytes, 2, id), payload, ())
            for id, payload in enumerate(share2_chunks_payloads)
        ]

        # Each cover contains all primary chunks of 1 share and all redundant chunks of the other share
        cover1_chunks_contents = share1_chunks_contents[:k] + share2_chunks_contents[k:]
        cover2_chunks_contents = share2_chunks_contents[:k] + share1_chunks_contents[k:]

        cover1_chunks = self.Chunk.create_all_chunks(
            cover1_chunks_contents, self.hmac_key
        )
        cover2_chunks = self.Chunk.create_all_chunks(
            cover2_chunks_contents, self.hmac_key
        )

        k_bytes = k.to_bytes(1, byteorder="big")
        stego_cover1 = self._embed_lsb332(k_bytes + b"".join(cover1_chunks), cover1)
        stego_cover2 = self._embed_lsb332(k_bytes + b"".join(cover2_chunks), cover2)

        return stego_cover1, stego_cover2

    def extract(self, stego_cover1: Img, stego_cover2: Img) -> str:
        share1_payloads: list[tuple[int, bytes]] = []
        share2_payloads: list[tuple[int, bytes]] = []

        cover1_bytes = self._img_bytes_lsb332(stego_cover1)
        cover2_bytes = self._img_bytes_lsb332(stego_cover2)

        k = int.from_bytes(cover1_bytes[:1], byteorder="big")
        redundancy = k // 2
        m = k + redundancy

        for offset in range(1, len(cover1_bytes), self.Chunk.chunk_size):
            chunk_bytes = cover1_bytes[offset : offset + self.Chunk.chunk_size]

            try:
                header_args, payload, _ = self.Chunk.unpack_and_verify_chunk(
                    chunk_bytes, self.hmac_key
                )
            except ValueError as e:
                print(e)
                continue

            _, share_id, chunk_id = header_args

            if share_id == 1:
                share1_payloads.append((chunk_id, payload))
            elif share_id == 2:
                share2_payloads.append((chunk_id, payload))
            else:
                print(f"Found {share_id=}, {chunk_id=}. Skipping...")
                continue

            if len(share1_payloads) == k and len(share2_payloads) == redundancy:
                break

        for offset in range(1, len(cover2_bytes), self.Chunk.chunk_size):
            chunk_bytes = cover2_bytes[offset : offset + self.Chunk.chunk_size]

            try:
                header_args, payload, _ = self.Chunk.unpack_and_verify_chunk(
                    chunk_bytes, self.hmac_key
                )
            except ValueError as e:
                print(e)
                continue

            _, share_id, chunk_id = header_args

            if share_id == 1:
                share1_payloads.append((chunk_id, payload))
            elif share_id == 2:
                share2_payloads.append((chunk_id, payload))
            else:
                print(f"Found {share_id=}, {chunk_id=}. Skipping...")
                continue

            if len(share1_payloads) == m and len(share2_payloads) == m:
                break

        share1 = recover_original_chunks(share1_payloads[:k], k, m)
        share2 = recover_original_chunks(share2_payloads[:k], k, m)

        message = combine_2_shares(b"".join(share1), b"".join(share2))
        # message contains extra nul b'\x00' bytes. Should we rstrip() it?
        return message

    def _img_bytes_lsb332(self, img: Img) -> bytes:
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

        return data.tobytes()

    def _embed_lsb332(self, data: bytes, img: Img) -> Img:
        mat = img.imgmatrix()
        height, width, _ = mat.shape
        capacity = height * width  # 1 byte per pixel

        # Pad remaining pixels with zero
        data += b"\x00" * (capacity - len(data))

        data_array = np.frombuffer(data, dtype=np.uint8)

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

    def _calculate_required_pixels(self, data_size: int, redundancy: int) -> int:
        """
        lsb332 stores 1 byte per pixel
        """
        primary_chunks = self.Chunk.calculate_required_chunks(data_size)
        total_chunks = primary_chunks + redundancy

        if total_chunks > 255:  # zfec limit
            raise ValueError("No. of total chunks for a share cannot be more than 255")

        total_overhead_bytes = total_chunks * self.Chunk.chunk_size

        return total_overhead_bytes

    def _validate_image_capacity(
        self, data_size: int, redundancy: int, available_pixels: int
    ):
        required_pixels = self._calculate_required_pixels(data_size, redundancy)
        if required_pixels > available_pixels:
            raise ValueError(
                f"Insufficient image capacity. "
                f"Required: {required_pixels} pixels, "
                f"Available: {available_pixels} pixels."
            )
