import os
import importlib.resources
from .wiipy.ciosbuild import build_cios

# Get the path to the d2xModules folder inside assets
d2x_modules = str(importlib.resources.files('src.libModMii.assets').joinpath('d2xModules'))

def buildD2XCios(entry, output_path, base_wad_path):
    # if os.path.exists(output_path):
    #     try:
    #         await verify_file(output_path, entry.md5, entry.md5alt)
    #         return f"WAD {entry.wadname} found in cache"
    #     except Exception:
    #         print('NUS: Cached file verification failed, re-downloading')
    if not entry.ciosslot or not entry.ciosversion:
        raise Exception(f"Missing cIOS slot or version for {entry.wadname}")
    if not os.path.exists(base_wad_path):
        raise Exception(f"Base WAD file not found: {base_wad_path}")
    
    cios_map_path = os.path.join(d2x_modules, "ciosmaps.xml")
    cios_version = entry.wadname[12:].replace('.wad', '')

    return build_cios(base_wad_path, cios_map_path, cios_version, d2x_modules, output_path, entry.ciosslot, entry.ciosversion)