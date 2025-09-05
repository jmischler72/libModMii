import json
import os
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class DatabaseEntry:
    name: str
    wadname: str
    md5: str
    code1: str
    code2: str
    version: Union[int, str]
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

# Define the path to the database.json file
db_path = os.path.join(os.getcwd(), 'database.json')

# Load the database
with open(db_path, 'r', encoding='utf-8') as f:
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