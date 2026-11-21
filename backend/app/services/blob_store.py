"""Content-addressed secure blob store with image sanitization.

Per §7.3 and ADR-0009:
- Max file size 8 MB.
- Content-addressed storage by SHA-256: data/blobs/ab/cd/<sha256>
- Images decoded and re-encoded with Pillow to strip EXIF, GPS, and neutralize polyglots.
- Dimension cap at 4096 x 4096.
"""

import hashlib
import io
from pathlib import Path
from PIL import Image

MAX_BLOB_SIZE_BYTES: int = 8 * 1024 * 1024  # 8 MB
MAX_IMAGE_DIMENSION: int = 4096

class BlobStoreError(Exception):
    """Raised when blob storage operations fail."""
    pass

class BlobStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, sha256_hex: str) -> Path:
        """Resolve content-addressed two-level directory path."""
        prefix1 = sha256_hex[:2]
        prefix2 = sha256_hex[2:4]
        return self.base_dir / prefix1 / prefix2 / sha256_hex

    def store_image(self, raw_bytes: bytes) -> tuple[str, int]:
        """Sanitize, strip EXIF metadata, re-encode, and store image content-addressed.

        Returns:
            (sha256_hex, final_size_bytes)
        """
        if len(raw_bytes) > MAX_BLOB_SIZE_BYTES:
            raise BlobStoreError(f"Blob size {len(raw_bytes)} exceeds limit of {MAX_BLOB_SIZE_BYTES} bytes")

        try:
            with Image.open(io.BytesIO(raw_bytes)) as img:
                # Strip metadata by extracting raw pixel data
                img.verify()
            
            # Re-open for actual processing after verification
            with Image.open(io.BytesIO(raw_bytes)) as img:
                width, height = img.size
                if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                    # Scale down while maintaining aspect ratio
                    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

                # Convert to RGB to neutralize RGBA/CMYK/palette attacks
                rgb_img = img.convert("RGB")
                out_buffer = io.BytesIO()
                # Re-encode to clean JPEG with quality 85
                rgb_img.save(out_buffer, format="JPEG", quality=85, optimize=True)
                sanitized_bytes = out_buffer.getvalue()

        except Exception as e:
            raise BlobStoreError(f"Failed to decode and sanitize image: {e}") from e

        sha256_hex = hashlib.sha256(sanitized_bytes).hexdigest()
        dest_path = self._get_path(sha256_hex)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            dest_path.write_bytes(sanitized_bytes)

        return sha256_hex, len(sanitized_bytes)

    def retrieve(self, sha256_hex: str) -> bytes | None:
        """Retrieve stored blob bytes by SHA-256 hash."""
        target_path = self._get_path(sha256_hex)
        if not target_path.is_file():
            return None
        return target_path.read_bytes()
