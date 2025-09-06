import hashlib
from typing import Optional


def verify_file(file_path: str, md5: Optional[str], md5alt: Optional[str] = None) -> None:
    if not md5 and not md5alt:
        raise Exception(f"No MD5 hash provided for file verification: {file_path}")

    with open(file_path, "rb") as f:
        file_buffer = f.read()

    hash_val = hashlib.md5(file_buffer).hexdigest()
    if hash_val == md5:
        return

    if md5alt and hash_val == md5alt:
        return

    raise Exception(
        f"File verification failed for {file_path}, expected MD5: {md5}, got: {hash_val}, alternative MD5: {md5alt}"
    )
