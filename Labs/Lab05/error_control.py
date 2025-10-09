# -------------------------------
# CRC IMPLEMENTATION
# -------------------------------
def xor_division(dividend, divisor):
    """Perform XOR division (used for CRC)."""
    pick = len(divisor)
    tmp = dividend[0:pick]

    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = xor_strings(divisor, tmp) + dividend[pick]
        else:
            tmp = xor_strings('0' * pick, tmp) + dividend[pick]
        pick += 1

    if tmp[0] == '1':
        tmp = xor_strings(divisor, tmp)
    else:
        tmp = xor_strings('0' * pick, tmp)

    return tmp


def xor_strings(a, b):
    """Helper XOR function for two binary strings."""
    result = []
    for i in range(1, len(b)):
        result.append(str(int(a[i]) ^ int(b[i])))
    return ''.join(result)


def crc_encode(data, generator="11011"):
    """Encode data with CRC using given generator."""
    appended_data = data + '0' * (len(generator) - 1)
    remainder = xor_division(appended_data, generator)
    codeword = data + remainder
    return codeword


def crc_verify(codeword, generator="11011"):
    """Verify CRC encoded data. Returns True if no error."""
    remainder = xor_division(codeword, generator)
    return set(remainder) == {'0'}


# -------------------------------
# HAMMING CODE (12,7) IMPLEMENTATION
# -------------------------------
def hamming_encode(data7):
    """Encode 7-bit data using Hamming (12,7)."""
    if len(data7) != 7:
        raise ValueError("Input must be 7 bits.")

    encoded = ['0'] * 12

    # Fill data bits into positions (skip parity positions 1,2,4,8)
    data_positions = [3, 5, 6, 7, 9, 10, 11]
    j = 0
    for pos in data_positions:
        encoded[pos - 1] = data7[j]
        j += 1

    # Calculate parity bits (at positions 1,2,4,8)
    for p in [1, 2, 4, 8]:
        parity = 0
        for i in range(1, 13):
            if i & p:
                parity ^= int(encoded[i - 1])
        encoded[p - 1] = str(parity)

    return ''.join(encoded)


def hamming_decode(encoded12):
    """Decode and correct single-bit error in Hamming (12,7)."""
    if len(encoded12) != 12:
        raise ValueError("Input must be 12 bits.")

    encoded = list(encoded12)
    error_pos = 0

    # Check parity bits
    for p in [1, 2, 4, 8]:
        parity = 0
        for i in range(1, 13):
            if i & p:
                parity ^= int(encoded[i - 1])
        if parity != 0:
            error_pos += p

    # Correct error if found
    if error_pos != 0:
        encoded[error_pos - 1] = '1' if encoded[error_pos - 1] == '0' else '0'

    # Extract original 7 data bits
    data_positions = [3, 5, 6, 7, 9, 10, 11]
    data_bits = [encoded[pos - 1] for pos in data_positions]

    return ''.join(data_bits), error_pos


# -------------------------------
# CHECKSUM IMPLEMENTATION
# -------------------------------
def checksum_gen(data, k=8):
    """Generate checksum for data (split into k-bit chunks)."""
    if len(data) % k != 0:
        data = data.zfill(((len(data) // k) + 1) * k)

    chunks = [data[i:i + k] for i in range(0, len(data), k)]
    total = 0
    for chunk in chunks:
        total += int(chunk, 2)
        total = (total & (2**k - 1)) + (total >> k)  # wraparound

    checksum = (~total) & (2**k - 1)
    return data + format(checksum, f'0{k}b')


def checksum_verify(received, k=8):
    """Verify checksum. Returns True if no error."""
    chunks = [received[i:i + k] for i in range(0, len(received), k)]
    total = 0
    for chunk in chunks:
        total += int(chunk, 2)
        total = (total & (2**k - 1)) + (total >> k)
    return total == (2**k - 1)


# -------------------------------
# SIMULATION
# -------------------------------
def simulate():
    print("=== CRC DEMO ===")
    data = "1101011011"
    codeword = crc_encode(data)
    print("Original Data:", data)
    print("CRC Encoded :", codeword)

    # Introduce error
    received = codeword[:5] + ('1' if codeword[5] == '0' else '0') + codeword[6:]
    print("Received (with error):", received)
    print("CRC Verify:", "No Error" if crc_verify(received) else "Error Detected")

    print("\n=== HAMMING CODE DEMO ===")
    msg = "1011001"
    encoded = hamming_encode(msg)
    print("Original 7-bit:", msg)
    print("Hamming Encoded:", encoded)

    # Introduce error at bit 5
    error_msg = encoded[:4] + ('1' if encoded[4] == '0' else '0') + encoded[5:]
    print("Received (with error):", error_msg)
    decoded, error_pos = hamming_decode(error_msg)
    print("Corrected Data:", decoded)
    print("Error Position:", error_pos if error_pos else "No Error")

    print("\n=== CHECKSUM DEMO ===")
    msg = "1010101010110011"
    packet = checksum_gen(msg)
    print("Original Message:", msg)
    print("With Checksum   :", packet)

    # Introduce error
    error_packet = packet[:8] + ('1' if packet[8] == '0' else '0') + packet[9:]
    print("Received (with error):", error_packet)
    print("Checksum Verify:", "No Error" if checksum_verify(error_packet) else "Error Detected")


if __name__ == "__main__":
    simulate()