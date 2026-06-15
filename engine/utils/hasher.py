import hashlib

def compute_hash(file_path: str) -> str:
    """
    Computes the SHA-256 hash of a file by reading it in chunks.
    This prevents memory overload for very large files.
    """
    sha256_hash = hashlib.sha256()
    
    # Read the file in 4MB chunks
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096 * 1024), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()
