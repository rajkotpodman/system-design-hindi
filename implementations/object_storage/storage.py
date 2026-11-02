"""
S3-like Object Storage with Block-Level Deduplication
Chapter 15: Design Google Drive & Chapter 24: S3-like Object Storage

Architecture:
1. Block-Level Chunking: Files are split into fixed-size chunks (e.g. 4MB or configurable size).
2. Content-Addressable Storage (CAS):
   - Each chunk's address is its cryptographic SHA-256 hash.
   - If two files or different versions of the same file share identical chunks,
     the chunk is saved only once (Data Deduplication).
3. Metadata Engine:
   - Stores object metadata: bucket_name, object_key, size, chunk hashes list.
4. Storage Efficiency:
   - Tracks saved disk space and deduplication ratio.
"""

from dataclasses import dataclass
import hashlib
import io
import threading
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ObjectMetadata:
    bucket: str
    key: str
    total_bytes: int
    chunk_hashes: List[str]
    created_at: float


class ObjectStorageService:
    """
    S3 / Google Drive Object Store with Content-Addressed Chunk Deduplication.
    """

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB default chunk
        self.chunk_size = chunk_size
        # chunk_hash -> bytes
        self._block_store: Dict[str, bytes] = {}
        # (bucket, key) -> ObjectMetadata
        self._metadata_store: Dict[Tuple[str, str], ObjectMetadata] = {}
        self._lock = threading.Lock()

    def put_object(self, bucket: str, key: str, data: bytes) -> ObjectMetadata:
        """
        Uploads an object, breaking it into deduplicated content-addressed chunks.
        """
        import time

        chunk_hashes: List[str] = []
        total_len = len(data)

        with self._lock:
            for offset in range(0, total_len, self.chunk_size):
                chunk = data[offset : offset + self.chunk_size]
                chunk_hash = hashlib.sha256(chunk).hexdigest()
                chunk_hashes.append(chunk_hash)

                if chunk_hash not in self._block_store:
                    self._block_store[chunk_hash] = chunk

            meta = ObjectMetadata(
                bucket=bucket,
                key=key,
                total_bytes=total_len,
                chunk_hashes=chunk_hashes,
                created_at=time.time(),
            )
            self._metadata_store[(bucket, key)] = meta
            return meta

    def get_object(self, bucket: str, key: str) -> Optional[bytes]:
        """
        Reassembles and returns full object bytes by stitching chunks in order.
        """
        with self._lock:
            meta = self._metadata_store.get((bucket, key))
            if not meta:
                return None

            buffer = io.BytesIO()
            for ch_hash in meta.chunk_hashes:
                chunk_bytes = self._block_store.get(ch_hash)
                if chunk_bytes is None:
                    raise IOError(f"Missing block chunk {ch_hash}!")
                buffer.write(chunk_bytes)

            return buffer.getvalue()

    def get_storage_stats(self) -> Dict[str, float]:
        """Calculates total logical stored data vs actual physical deduplicated storage."""
        with self._lock:
            total_logical_bytes = sum(m.total_bytes for m in self._metadata_store.values())
            total_physical_bytes = sum(len(b) for b in self._block_store.values())

            dedup_savings_bytes = max(0, total_logical_bytes - total_physical_bytes)
            dedup_ratio = (
                round(total_logical_bytes / total_physical_bytes, 2)
                if total_physical_bytes > 0
                else 1.0
            )

            return {
                "total_objects": len(self._metadata_store),
                "unique_blocks": len(self._block_store),
                "logical_bytes": total_logical_bytes,
                "physical_bytes": total_physical_bytes,
                "saved_bytes": dedup_savings_bytes,
                "deduplication_ratio": dedup_ratio,
            }

