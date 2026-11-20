import secrets

# def split_n_shares(str, n: int): pass # todo: split into n shares


def split_2_shares(secret_message: str) -> tuple[bytes, bytes]:
    """
    Converts a secret string into UTF-8 bytes and splits it into two
    2-out-of-2 XOR shares using a cryptographically secure random pad.
    """
    # 1. Convert the message string into UTF-8 bytes
    secret_bytes = secret_message.encode("utf-8")
    length = len(secret_bytes)

    # 1.5: todo?: set random seed for generating share1. instead of embedding share1, embed encrypted seed?

    # 2. Generate Share 1: Pure random bytes of the exact same length
    share1 = secrets.token_bytes(length)

    # 3. Generate Share 2: Bitwise XOR between Share 1 and the secret UTF-8 bytes
    share2 = bytes(s1 ^ sb for s1, sb in zip(share1, secret_bytes))

    return share1, share2


def combine_2_shares(share1: bytes, share2: bytes) -> str:
    """
    Combines both byte shares via bitwise XOR and decodes back to UTF-8 text.
    """
    if len(share1) != len(share2):
        raise ValueError("Shares must have the exact same byte length.")

    recovered_bytes = bytes(s1 ^ s2 for s1, s2 in zip(share1, share2))
    return recovered_bytes.decode("utf-8")
