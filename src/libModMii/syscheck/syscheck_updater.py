from typing import Dict, Any, Optional
from dataclasses import dataclass
from . import info_helpers as info
from . import validation_helpers as validation

class SyscheckError(Exception):
    pass

@dataclass
class SyscheckInfos:
    region: str
    hbcVersion: Optional[str]
    systemMenuVersion: Optional[str]
    firmware: Dict[str, str]
    consoleType: str

def get_syscheck_infos(data: str) -> SyscheckInfos:
    data = validation.translate_keywords_to_english(data)
    
    if not validation.validate_syscheck_data(data):
        raise SyscheckError('The CSV file is not a valid SysCheck report')

    region = info.get_console_region(data)
    hbc_version = info.get_hbc_version(data)
    system_menu_version = info.get_system_menu_version(data)
    firmware = info.get_firmware(system_menu_version) if system_menu_version else None
    console_type = info.get_console_type(data)

    if not region or not system_menu_version or not firmware:
        raise SyscheckError('Could not extract necessary information from the CSV file')

    if not console_type or not validation.validate_console_type(console_type):
        raise SyscheckError('The CSV file does not contain a valid console type')

    region_short_code = info.get_region_short_code(region)
    if firmware['SMregion'] != region_short_code:
        raise SyscheckError(
            f'The firmware region "{firmware["SMregion"]}" does not match the console region "{region_short_code}"'
        )

    return SyscheckInfos(
        region=region,
        hbcVersion=hbc_version,
        systemMenuVersion=system_menu_version,
        firmware={
            'SMregion': firmware['SMregion'],
            'firmware': firmware['firmware'],
            'firmwareVersion': firmware['firmwareVersion'],
        },
        consoleType=console_type
    )

def get_syscheck_analysis(data: str, activeIOS: bool = False, extraProtection: bool = False) -> Dict[str, Any]:
    infos = get_syscheck_infos(data)
    
    wad_to_install = []

    # Check system components
    is_bootmii_installed = validation.check_if_bootmii_installed(data)
    is_priiloader_installed = validation.check_if_priiloader_installed(data)
    is_hbc_outdated = validation.check_if_hbc_is_outdated(infos.hbcVersion, infos.consoleType) if infos.hbcVersion else False
    outdated_d2xcios = validation.check_d2x_cios(data, infos.consoleType)
    missing_ios = validation.check_for_missing_ios(data, infos.region, infos.consoleType) if activeIOS else []
    needs_extra_protection = validation.check_extra_protection(data) if extraProtection else []

    if not is_bootmii_installed:
        wad_to_install.append('HM')
    else:
        if not infos.hbcVersion:
            wad_to_install.append('OHBC113')
            # also check if IOS58 is installed
            is_ios58_installed = 'IOS58' in data
            if not is_ios58_installed and is_bootmii_installed:
                wad_to_install.append('IOS58')
        else:
            if is_hbc_outdated:
                wad_to_install.append('OHBC')

    latest_firmware_version = info.get_latest_sm_version(infos.firmware)
    if latest_firmware_version != infos.firmware['firmware']:
        wad_to_install.append(f'SM{latest_firmware_version}{infos.firmware["SMregion"]}')

    update_priiloader = False
    if not is_priiloader_installed or (is_priiloader_installed and update_priiloader):
        wad_to_install.append('prii')

    wad_to_install.extend(outdated_d2xcios)

    if activeIOS:
        wad_to_install.extend(missing_ios)

    if extraProtection:
        wad_to_install.extend(needs_extra_protection)

    if wad_to_install:
        wad_to_install.append('yawm')

    return wad_to_install
