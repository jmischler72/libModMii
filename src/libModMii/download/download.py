import os
import hashlib
from typing import List, Optional, Dict, Any
from download.validation import verify_file
from download.osc_download import osc_download
from download.wiipy.nus import nus_title_download
from database import get_database_entry
from download.d2xbuild import buildD2XCios

TEMP_DIRECTORY = os.environ.get("TEMP_DIRECTORY") or os.path.join(os.getcwd(), "temp-downloads")

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


def download_entry(entry: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    database_entry = get_database_entry(entry)
    if not database_entry:
        raise Exception(f"No entry found in database for {entry}")

    print(f"Downloading: {database_entry.wadname}")

    if output_path is None:
        temp_path = ensure_temp_directory()
        output_path = temp_path
        
    entry_path = os.path.join(output_path, database_entry.wadname)

    if not database_entry.category and not database_entry.ciosslot:
        raise Exception(f"Unsupported category for download: {database_entry.category}")

    # Handle download based on category
    if database_entry.category == "ios":
        nus_title_download(
            tid=f"{database_entry.code1}{database_entry.code2}",
            version=database_entry.version,
            wad=entry_path,
            verbose=False
        )
    elif database_entry.category == "OSC":
        osc_download(database_entry, entry_path)
    elif database_entry.category == "d2x":
        base_entry_path = os.path.join(output_path, database_entry.basewad) + ".wad"
        nus_title_download(
            tid=f"{database_entry.code1}{database_entry.code2}",
            version=database_entry.version,
            wad=base_entry_path,
            verbose=False
        )
        print(f"Base WAD downloaded: {database_entry.basewad}")
        verify_file(base_entry_path, database_entry.md5base, database_entry.md5basealt)
        buildD2XCios(database_entry, entry_path, base_entry_path)
        # elif database_entry["category"] == "patchios":
        #     base_wad_path = f"/tmp/{database_entry['basewad']}.wad"
        #     base_entry = get_database_entry_from_wadname(database_entry["basewad"])
        #     if not base_entry:
        #         raise Exception(f"Base WAD entry not found: {database_entry['basewad']}")
        #     await nus_download(base_entry, base_wad_path)
        #     await verify_file(base_wad_path, database_entry.get("md5base"), database_entry.get("md5basealt"))
        #     await patch_ios(database_entry, output_path, base_wad_path)

    # Verify the final output file
    if not entry_path or not os.path.exists(entry_path):
        raise Exception(f"File was not created after download: {database_entry.wadname}")
    
    if database_entry.md5:
        verify_file(entry_path, database_entry.md5, database_entry.md5alt)

    print(f"Download completed: {database_entry.wadname}")
    return {
        "wadname": database_entry.wadname,
        "outputPath": output_path
    }

def download_entries(entries:List[str]):
    total = len(entries)

    print(f"Starting download of {total} WAD files...")

    for i in range(0, len(entries), 1):
        try:
            entry = download_entry(entries[i])
            print(f"Downloaded {entry['wadname']} to {entry['outputPath']}")
        except Exception as error:
            print(f"Error downloading {entries[i]}: {error}")