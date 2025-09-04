import re
from typing import Optional

class CustomError(Exception):
    pass

def get_console_region(data: str) -> Optional[str]:
    region_line = next((line for line in data.split('\n') if line.strip().lower().startswith('region:')), None)
    if not region_line:
        return None

    region = region_line.split(':', 1)[1].strip().upper()

    if region == 'PAL':
        return 'PAL'
    if region == 'NTSC-U':
        return 'NTSC-U'
    if region in ('NTSC-J', 'JAP'):
        return 'NTSC-J'
    if region == 'KOR':
        return 'KOR'

    return None

def get_region_short_code(region: str) -> str:
    if region == 'PAL':
        return 'E'
    elif region == 'NTSC-U':
        return 'U'
    elif region == 'NTSC-J':
        return 'J'
    elif region == 'KOR':
        return 'K'
    else:
        return region

def get_hbc_version(data: str) -> Optional[str]:
    hbc_line = next((line for line in data.split('\n') if 'Homebrew Channel' in line), None)
    if not hbc_line:
        return None

    match = re.search(r'Homebrew Channel\s+([0-9.]+)', hbc_line)
    return match.group(1) if match else None

def get_system_menu_version(data: str) -> Optional[str]:
    system_menu_line = next((line for line in data.split('\n') if 'System Menu' in line), None)
    if not system_menu_line:
        return None

    version = re.sub(r'^.*System Menu\s*', '', system_menu_line)
    version = version.strip().replace(',', '')
    return version or None

def get_firmware(system_menu_version: str) -> Optional[dict[str, object]]:
    firmstart = re.sub(r'\(.*?\)', '', system_menu_version).strip()
    firmend = re.search(r'\((.*?)\)', system_menu_version)
    firmend_parsed = int(firmend.group(1).replace('v', '')) if firmend else 0

    SMregion = firmstart[-1]
    firmstart = firmstart[:-1]

    if firmstart.startswith('3'):
        firmstart = '3.X'
    elif firmstart.startswith('2') or firmstart.startswith('1'):
        firmstart = 'o'

    return {'firmware': firmstart, 'firmwareVersion': firmend_parsed, 'SMregion': SMregion}

def get_latest_sm_version(data: dict[str, object]) -> str:
    if data['firmwareVersion'] in (4609, 4610):
        raise CustomError('This SysCheck is for a Wii Mini and is not currently supported, aborting analysis')

    if data['firmwareVersion'] > 518:
        if data['firmware'] in ('4.2', '4.1'):
            return data['firmware']
        return '4.3'

    if data['firmware'] in ('4.0', '3.X', 'o'):
        return '4.3'
    else:
        return data['firmware']

def get_console_type(data: str) -> Optional[str]:
    console_type_line = next((line for line in data.split('\n') if 'Console Type' in line), None)
    if not console_type_line:
        return None

    console_type = console_type_line.split(':', 1)[1].strip()
    return console_type
