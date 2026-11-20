import zfec


def generate_redundant_chunks(
    data_chunks: list[bytes], redundancy: int | None = None
) -> list[bytes]:
    k = len(data_chunks)

    if not redundancy:
        redundancy = k // 2

    m = k + redundancy

    encoder = zfec.Encoder(k=k, m=m)
    encoded_chunks = encoder.encode(data_chunks)

    return encoded_chunks


def recover_original_chunks(
    received_chunks: list[tuple[int, bytes]], k: int, m: int
) -> list[bytes]:
    """
    @param received_chunks: k size list of tuples of form: (chunk_id, chunk_data).
    """

    chunks = [chunk for _, chunk in received_chunks]
    chunk_ids = [chunk_id for chunk_id, _ in received_chunks]

    decoder = zfec.Decoder(k=k, m=m)
    decoded_chunks = decoder.decode(chunks, chunk_ids)

    return decoded_chunks
