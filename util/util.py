def split_string(string: str, chunk_size: int) -> list[str]:
    words = string.split()
    result = []
    current_chunk = ""
    for word in words:
        if (len(current_chunk) + len(word) + 1 <= chunk_size):  # Check if adding the word exceeds the chunk size
            current_chunk += " " + word
        else:
            if current_chunk:  # Append the current chunk if not empty
                result.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:  # Append the last chunk if not empty
        result.append(current_chunk.strip())
    return result
