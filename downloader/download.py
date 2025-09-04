import os
import shutil
import hashlib
from typing import List, Optional, Dict, Any
from helpers.database_helper import get_database_entry, get_database_entry_from_wadname
from helpers.wiipy_wrapper import build_cios, nus_download, patch_ios
from osc_download import osc_download

from helpers.s3_storage import (
    file_exists_in_s3,
    upload_file_to_s3,
    generate_wad_s3_key,
    generate_presigned_url,
)

TEMP_DIRECTORY = os.environ.get("TEMP_DIRECTORY") or os.path.join(os.getcwd(), "temp-downloads")


class DownloadResult:
    def __init__(
        self,
        success: bool,
        wadname: str,
        cached: bool,
        s3Key: Optional[str] = None,
        s3Url: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.wadname = wadname
        self.cached = cached
        self.s3Key = s3Key
        self.s3Url = s3Url
        self.error = error


class DownloadSummary:
    def __init__(
        self,
        totalRequested: int,
        downloaded: int,
        cached: int,
        failed: int,
        results: List[DownloadResult],
    ):
        self.totalRequested = totalRequested
        self.downloaded = downloaded
        self.cached = cached
        self.failed = failed
        self.results = results


def ensure_temp_directory() -> str:
    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    return TEMP_DIRECTORY


def cleanup_temp_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as error:
        print(f"Failed to cleanup temp file {file_path}: {error}")


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


async def download_wad_file(entry: Dict[str, Any], output_path: str):
    if not entry.get("category") and not entry.get("ciosslot"):
        raise Exception(f"Unsupported category for download: {entry.get('category')}")

    if entry["category"] in ("cios", "d2x"):
        base_wad_path = f"/tmp/{entry['basewad']}.wad"
        await nus_download(entry, base_wad_path)
        await verify_file(base_wad_path, entry.get("md5base"), entry.get("md5basealt"))
        await build_cios(entry, output_path, base_wad_path)
    else:
        if entry["category"] == "ios":
            await nus_download(entry, output_path)
        elif entry["category"] == "OSC":
            await osc_download(entry, output_path)
        elif entry["category"] == "patchios":
            base_wad_path = f"/tmp/{entry['basewad']}.wad"
            base_entry = get_database_entry_from_wadname(entry["basewad"])
            if not base_entry:
                raise Exception(f"Base WAD entry not found: {entry['basewad']}")
            await nus_download(base_entry, base_wad_path)
            await verify_file(base_wad_path, entry.get("md5base"), entry.get("md5basealt"))
            await patch_ios(entry, output_path, base_wad_path)

    if not entry.get("md5") and entry["category"] == "OSC":
        return
    await verify_file(output_path, entry.get("md5"), entry.get("md5alt"))


async def handle_download_wad_file(wad_id: str) -> DownloadResult:
    database_entry = get_database_entry(wad_id)
    if not database_entry:
        raise Exception(f"No entry found in database for {wad_id}")
    print(f"Downloading: {database_entry.get('wadname')}")

    s3_key = generate_wad_s3_key(database_entry["wadname"])
    exists_in_s3 = await file_exists_in_s3(s3_key)

    if not exists_in_s3:
        temp_path = ensure_temp_directory()
        output_path = os.path.join(temp_path, database_entry["wadname"])
        await download_wad_file(database_entry, output_path)

        if not output_path or not os.path.exists(output_path):
            raise Exception(f"File was not created after download: {database_entry['wadname']}")

        await upload_file_to_s3(output_path, s3_key, "application/octet-stream")
        cleanup_temp_file(output_path)
        print(f"Successfully uploaded {database_entry['wadname']} to S3")

    presigned_url = await generate_presigned_url(s3_key, 86400)

    return DownloadResult(
        success=True,
        wadname=database_entry["wadname"],
        cached=exists_in_s3,
        s3Key=s3_key,
        s3Url=presigned_url,
    )


async def handle_download_multiple_wads(
    wad_ids: List[str],
    options: Optional[Dict[str, Any]] = None,
) -> DownloadSummary:
    if options is None:
        options = {}
    max_concurrent = options.get("maxConcurrent", 3)
    results: List[DownloadResult] = []
    total = len(wad_ids)

    print(f"Starting download of {total} WAD files...")

    for i in range(0, len(wad_ids), max_concurrent):
        batch = wad_ids[i : i + max_concurrent]
        batch_results = []
        for wad_id in batch:
            try:
                result = await handle_download_wad_file(wad_id)
            except Exception as error:
                print(f"Error downloading {wad_id}: {error}")
                result = DownloadResult(success=False, wadname=wad_id, cached=False)
            batch_results.append(result)
        results.extend(batch_results)

    summary = DownloadSummary(
        totalRequested=total,
        downloaded=len([r for r in results if r.success and not r.cached]),
        cached=len([r for r in results if r.success and r.cached]),
        failed=len([r for r in results if not r.success]),
        results=results,
    )

    print(
        f"Download summary: {summary.downloaded} downloaded, {summary.cached} cached, {summary.failed} failed"
    )

    if summary.failed > 0:
        failed_files = [r.wadname for r in results if not r.success]
        print(f"Failed downloads: {', '.join(failed_files)}")

    return summary
