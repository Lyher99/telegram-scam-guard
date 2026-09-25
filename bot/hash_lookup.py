import os
import re
import logging

logger = logging.getLogger(__name__)

_local_db = None
_file_info = None

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def _load_local_db():
    global _local_db, _file_info

    if _local_db is not None:
        return

    _local_db = set()
    _file_info = {}

    csv_path = os.path.join(DATA_DIR, "malwarebazaar.csv")
    if not os.path.exists(csv_path):
        logger.warning("MalwareBazaar CSV not found, hash lookup disabled")
        return

    with open(csv_path, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue

            hashes = re.findall(r"[0-9a-f]{64}", line.lower())
            if not hashes:
                continue

            sha256 = hashes[0]
            _local_db.add(sha256)

            parts = line.split(",")

            def clean(s):
                return s.strip().strip('"').strip().strip('"').strip()

            file_name = clean(parts[5]) if len(parts) > 5 else "unknown"
            file_type = clean(parts[6]) if len(parts) > 6 else "unknown"
            signature = clean(parts[8]) if len(parts) > 8 else "unknown"

            _file_info[sha256] = {
                "file_name": file_name,
                "file_type": file_type,
                "signature": signature,
            }

    logger.info(f"Loaded {len(_local_db)} hashes from local MalwareBazaar DB")


async def check_hash(sha256_hash):
    if not sha256_hash or len(sha256_hash) != 64:
        return {"found": False, "error": "Invalid hash format"}

    _load_local_db()

    if _local_db is None:
        return {"found": False, "error": "Local database not available"}

    sha256_lower = sha256_hash.lower()

    if sha256_lower in _local_db:
        info = _file_info.get(sha256_lower, {})
        return {
            "found": True,
            "file_type": info.get("file_type", "unknown"),
            "file_name": info.get("file_name", "unknown"),
            "signature": info.get("signature", "unknown"),
            "first_seen": "recent",
            "tags": [],
        }

    return {"found": False}


def get_db_size():
    _load_local_db()
    return len(_local_db) if _local_db else 0
