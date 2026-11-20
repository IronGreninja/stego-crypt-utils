import hashlib
import hmac
import struct
from collections.abc import Iterable

from numpy import datetime_as_string


class Chunk:
    """
    chunk format:
        header
        payload
        hmac(header + payload)
        trailer(optional)
    """

    def __init__(
        self, header_format: str, payload_size: int, trailer_format: str
    ) -> None:
        self.header_format = header_format
        self.header_size = struct.calcsize(header_format)
        self.payload_size = payload_size
        self.hmac_size = 32  # we use hmac-sha-256
        self.trailer_format = trailer_format
        self.trailer_size = struct.calcsize(trailer_format)
        self.chunk_size = (
            self.header_size + self.payload_size + self.hmac_size + self.trailer_size
        )

    def build_header(self, *args) -> bytes:
        header = struct.pack(self.header_format, *args)
        return header

    def build_trailer(self, *args) -> bytes:
        trailer = struct.pack(self.trailer_format, *args)
        return trailer

    def parse_header(self, header_bytes: bytes) -> tuple:
        # Check whether the supplied header has the correct size.
        if len(header_bytes) != self.header_size:
            raise ValueError("Invalid header size.")

        # Unpack the header into its original fields.
        header_args = struct.unpack(self.header_format, header_bytes)

        return header_args

    def parse_trailer(self, trailer_bytes: bytes) -> tuple:
        if len(trailer_bytes) != self.trailer_size:
            raise ValueError("Invalid trailer size.")

        trailer_args = struct.unpack(self.trailer_format, trailer_bytes)

        return trailer_args

    def compute_chunk_hmac(
        self, header: bytes, payload: bytes, hmac_key: bytes
    ) -> bytes:
        # Create an HMAC object using SHA-256.
        mac = hmac.new(hmac_key, digestmod=hashlib.sha256)

        # Include the header in authentication.
        mac.update(header)

        # Include the actual payload in authentication.
        mac.update(payload)

        # Return the 32-byte authentication tag.
        return mac.digest()

    def create_single_chunk(
        self,
        header_args: Iterable,
        payload: bytes,
        hmac_key: bytes,
        trailer_args: Iterable,
    ) -> bytes:

        if len(payload) != self.payload_size:
            raise ValueError(f"Payload must contain {self.payload_size} bytes.")

        # Generate the header.
        header = self.build_header(*header_args)

        # Generate the HMAC.
        hmac = self.compute_chunk_hmac(header, payload, hmac_key)

        # Generate trailer
        trailer = self.build_trailer(*trailer_args)

        # Combine
        chunk = header + payload + hmac + trailer

        return chunk

    def create_all_chunks(
        self, contents: Iterable[tuple[tuple, bytes, tuple]], hmac_key: bytes
    ) -> list[bytes]:
        """
        @param contents: iterable of iterables of the form (header_args, payload, trailer_args)
        """

        chunks = []

        for header_args, payload, trailer_args in contents:
            chunks.append(
                self.create_single_chunk(header_args, payload, hmac_key, trailer_args)
            )

        return chunks

    def unpack_and_verify_chunk(
        self, chunk_bytes: bytes, hmac_key: bytes
    ) -> tuple[tuple, bytes, tuple]:
        """
        Extracts and verifies a serialized chunk.

        This function expects the exact serialized chunk bytes.
        For example, it must not receive extra padding bytes.

        Returns tuples of header_args, payload and trailer_args if succesful.
        """

        if len(chunk_bytes) != self.chunk_size:
            raise ValueError("Chunk size invalid.")

        header = chunk_bytes[: self.header_size]

        payload = chunk_bytes[self.header_size : self.header_size + self.payload_size]

        hmac_bytes = chunk_bytes[
            self.header_size + self.payload_size : self.header_size
            + self.payload_size
            + self.hmac_size
        ]

        trailer = chunk_bytes[-self.trailer_size :] if self.trailer_size > 0 else b""

        # Validate and parse the header.
        header_args = self.parse_header(header)
        trailer_args = self.parse_trailer(trailer)

        # Recalculate the expected HMAC.
        expected_hmac = self.compute_chunk_hmac(header, payload, hmac_key)

        # Compare the received and calculated HMAC securely.
        if not hmac.compare_digest(hmac_bytes, expected_hmac):
            raise ValueError(
                f"HMAC verification failed for chunk. chunk header args: {header_args}."
            )

        # Return the verified chunk information.
        return header_args, payload, trailer_args

    def calculate_required_chunks(self, data_size: int) -> int:
        return (data_size + self.payload_size - 1) // self.payload_size

    def split_payload(self, payload: bytes) -> list[bytes]:
        payload_splits = [
            payload[offset : offset + self.payload_size]
            for id, offset in enumerate(range(0, len(payload), self.payload_size))
        ]

        if (_len := len(payload_splits[-1])) != self.payload_size:
            payload_splits[-1] += bytes(self.payload_size - _len)

        return payload_splits
