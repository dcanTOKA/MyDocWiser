import hashlib
import os


def get_unique_filename(url: str, output_dir: str) -> str:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(output_dir, f"{os.path.basename(url)}_{url_hash}.pdf")
