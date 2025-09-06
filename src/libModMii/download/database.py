import json
import importlib.resources
import os
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class DatabaseEntry:
    name: str
    wadname: str
    code1: str
    md5: Optional[str] = None
    version: Optional[int] = None
    code2: Optional[str] = None
    code2new: Optional[str] = None
    md5alt: Optional[str] = None
    category: Optional[str] = None
    dlname: Optional[str] = None
    filename: Optional[str] = None
    basecios: Optional[str] = None
    ciosslot: Optional[str] = None
    ciosversion: Optional[str] = None
    basewad: Optional[str] = None
    md5base: Optional[str] = None
    md5basealt: Optional[str] = None
    diffpath: Optional[str] = None
    lastbasemodule: Optional[str] = None
    cIOSFamilyName: Optional[str] = None
    cIOSversionNum: Optional[int] = None


# Load the database.json from the assets folder using importlib.resources
with importlib.resources.files('libModMii.assets').joinpath('database.json').open('r', encoding='utf-8') as f:
    database = json.load(f)

def get_database_entry(entry: str) -> DatabaseEntry:
    entry_data = database['entries'].get(entry)
    if entry_data and not os.path.splitext(entry_data['wadname'])[1]:
        entry_data['wadname'] += '.wad'
    return DatabaseEntry(**entry_data)

def get_database_entry_from_wadname(wadname: str) -> Optional[DatabaseEntry]:
    if not wadname.endswith('.wad'):
        wadname += '.wad'
    for entry in database['entries'].values():
        if entry['wadname'] == wadname:
            return DatabaseEntry(**entry)
    return None

def get_all_entries() -> dict:
    return database['entries']