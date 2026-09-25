import os
import io
import zipfile
import logging

logger = logging.getLogger(__name__)

DANGEROUS_EXTS = {
    ".exe", ".scr", ".bat", ".cmd", ".com", ".msi", ".js", ".vbs",
    ".jar", ".apk", ".lnk", ".ps1", ".hta", ".pif", ".dll", ".reg", ".sh",
}

SUSPICIOUS_EXTS = {
    ".zip", ".rar", ".7z", ".iso", ".img",
}


def check_zip_contents(file_bytes):
    results = {
        "is_zip": False,
        "total_files": 0,
        "dangerous_files": [],
        "suspicious_files": [],
        "all_extensions": [],
        "has_double_ext": False,
    }

    if not zipfile.is_zipfile(io.BytesIO(file_bytes)):
        return results

    results["is_zip"] = True

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue

                results["total_files"] += 1
                name = info.filename
                ext = os.path.splitext(name)[1].lower()
                results["all_extensions"].append(ext)

                parts = name.split(".")
                if len(parts) >= 3:
                    results["has_double_ext"] = True

                if ext in DANGEROUS_EXTS:
                    results["dangerous_files"].append(name)
                elif ext in SUSPICIOUS_EXTS:
                    results["suspicious_files"].append(name)

    except zipfile.BadZipFile:
        results["is_zip"] = False
    except Exception as e:
        logger.error(f"ZIP check error: {e}")

    return results
