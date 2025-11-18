def return_file_size(reader) -> int:
    start = reader.tell()
    end = reader.size()

    data = reader.read_bytes(end - start)

    result = data.tobytes().find(b"\xAD\xDE\xAD\xDE")

    if result == -1:
        return
    
    reader.skip(start)

    return result
    
def find_next_file(reader) -> None:
    start = reader.tell()
    end = reader.size()

    data = reader.read_bytes(end - start)

    result = data.tobytes().find(b"\xAD\xDE\xAD\xDE")

    if result == -1:
        return
    
    reader.skip(start)

    reader.read_bytes(result)