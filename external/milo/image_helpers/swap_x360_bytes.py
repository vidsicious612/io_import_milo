def swap_x360_bytes(bitmap: bytes) -> bytes:
    flipped_bitmap = bytearray()

    for i in range(0, len(bitmap), 2):
        flipped_bitmap.append(bitmap[i + 1])
        flipped_bitmap.append(bitmap[i])
            
    return bytes(flipped_bitmap)