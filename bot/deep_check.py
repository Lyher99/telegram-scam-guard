import os
import hashlib
import logging

logger = logging.getLogger(__name__)

MAGIC_SIGNATURES = [
    (b"MZ", "exe/dll", ".exe"),
    (b"PK", "zip/jar", ".zip"),
    (b"\x7fELF", "linux_elf", ".elf"),
    (b"\x1f\x8b", "gzip", ".gz"),
    (b"%PDF", "pdf", ".pdf"),
    (b"\xd0\xcf\x11\xe0", "ms_office", ".doc"),
    (b"Rar!", "rar", ".rar"),
    (b"7z\xbc\xaf\x27\x1c", "7z", ".7z"),
    (b"\x89PNG", "png", ".png"),
    (b"\xff\xd8\xff", "jpeg", ".jpg"),
    (b"GIF8", "gif", ".gif"),
    (b"RIFF", "webp_or_video", ".webp"),
    (b"ID3", "mp3_audio", ".mp3"),
    (b"\x00\x00\x00", "iso_or_unknown", None),
    (b"BM", "bmp_image", ".bmp"),
]

DANGEROUS_REAL_TYPES = {"exe/dll", "linux_elf"}

EXT_TO_REAL = {
    ".exe": {"exe/dll"},
    ".scr": {"exe/dll"},
    ".bat": set(),
    ".cmd": set(),
    ".com": {"exe/dll"},
    ".msi": {"exe/dll"},
    ".js": set(),
    ".vbs": set(),
    ".jar": {"zip/jar"},
    ".apk": {"zip/jar"},
    ".lnk": set(),
    ".ps1": set(),
    ".hta": set(),
    ".pif": {"exe/dll"},
    ".dll": {"exe/dll"},
    ".reg": set(),
    ".sh": set(),
    ".pdf": {"pdf"},
    ".doc": {"ms_office"},
    ".docx": {"ms_office"},
    ".xls": {"ms_office"},
    ".xlsx": {"ms_office"},
    ".ppt": {"ms_office"},
    ".pptx": {"ms_office"},
    ".jpg": {"jpeg"},
    ".jpeg": {"jpeg"},
    ".png": {"png"},
    ".gif": {"gif"},
    ".bmp": {"bmp_image"},
    ".zip": {"zip/jar"},
    ".rar": {"rar"},
    ".7z": {"7z"},
    ".gz": {"gzip"},
    ".mp3": {"mp3_audio"},
    ".mp4": {"mp4_or_unknown"},
    ".avi": {"mp4_or_unknown"},
    ".mkv": {"mp4_or_unknown"},
    ".txt": set(),
    ".csv": set(),
    ".rtf": set(),
}


def deep_check_file(file_bytes, declared_ext=None):
    results = {
        "sha256": None,
        "real_type": "unknown",
        "declared_ext": declared_ext,
        "extension_mismatch": False,
        "dangerous_type": False,
        "file_size_bytes": len(file_bytes),
    }

    if len(file_bytes) >= 4:
        header = file_bytes[:8]
        for magic, real_type, real_ext in MAGIC_SIGNATURES:
            if header[: len(magic)] == magic:
                results["real_type"] = real_type
                break

    if results["real_type"] in DANGEROUS_REAL_TYPES:
        results["dangerous_type"] = True

    if declared_ext and declared_ext in EXT_TO_REAL:
        expected_types = EXT_TO_REAL[declared_ext]
        if expected_types and results["real_type"] not in expected_types:
            results["extension_mismatch"] = True

    return results
