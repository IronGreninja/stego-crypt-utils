DELIMITER_BYTES = bytes([0xFF, 0xFE, 0xFF, 0xFE])
DELIMITER = ''.join(f'{b:08b}' for b in DELIMITER_BYTES)  # 32 bits
def text_to_bits(text):
    payload = ''.join(f'{byte:08b}' for byte in text.encode('utf-8'))
    return payload + DELIMITER

def bits_to_text(bits):
    stop = bits.find(DELIMITER)
    if stop == -1:
        raise ValueError("No end-of-message sentinel found.")
    payload = bits[:stop]
    trim = len(payload) - (len(payload) % 8)
    chars = [payload[i:i+8] for i in range(0, trim, 8)]
    return bytes(int(c, 2) for c in chars).decode('utf-8')