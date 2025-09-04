from typing import Dict, Any, List, Optional, Tuple, Union

class CustomError(Exception):
    pass

def upload_syscheck_file(form_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        file = form_data.get('file')
        active_ios_str = form_data.get('activeIOS')
        extra_protection_str = form_data.get('extraProtection')

        # Validate the form data using the shared schema
        validation_result = upload_form_data_schema_safe_parse({
            'file': file,
            'activeIOS': active_ios_str,
            'extraProtection': extra_protection_str,
        })

        if not validation_result['success']:
            raise CustomError(validation_result['error']['issues'][0]['message'])

        validated_file = validation_result['data']['file']
        active_ios = validation_result['data']['activeIOS']
        extra_protection = validation_result['data']['extraProtection']
        c_mios = False  # A cMIOS allows older non-chipped Wii's to play GameCube backup discs

        csv_content = validated_file.read().decode('utf-8')

        if not csv_content.strip():
            raise CustomError('The CSV file appears to be empty')

        # copy csv to copydata
        copy_data = csv_content

        copy_data = translate_keywords_to_english(copy_data)

        if not validate_syscheck_data(copy_data):
            raise CustomError('The CSV file is not a valid SysCheck report')

        system_infos = handle_syscheck_data(copy_data, {
            'activeIOS': active_ios,
            'extraProtection': extra_protection,
            'cMios': c_mios
        })

        wads_infos = []
        for wad_id in system_infos['wadToInstall']:
            entry = get_database_entry(wad_id)
            wadname = entry['wadname'] if entry and 'wadname' in entry else 'Unknown'
            wads_infos.append({'wadname': wadname, 'wadId': wad_id})

        return {
            'success': True,
            'message': f'CSV file "{validated_file.name}" uploaded successfully',
            'data': {
                'filename': validated_file.name,
                'size': validated_file.size,
                'region': system_infos.get('region', 'Unknown'),
                'hbcVersion': system_infos.get('hbcVersion', 'Unknown'),
                'systemMenuVersion': system_infos.get('systemMenuVersion', 'Unknown'),
                'firmware': system_infos['firmware'],
                'consoleType': system_infos['consoleType'],
                'systemChecks': system_infos['systemChecks'],
                'wadsInfos': wads_infos or [],
            },
        }
    except Exception as error:
        print('Error processing CSV file:', error)
        return {
            'success': False,
            'error': str(error) if isinstance(error, CustomError) else 'An error occurred while processing the syscheck file',
        }

def handle_syscheck_data(
    data: str,
    options: Dict[str, Any]
) -> Dict[str, Any]:
    options['extraProtection'] = False  # Extra protection is disabled for now

    region = get_console_region(data)
    hbc_version = get_hbc_version(data)
    system_menu_version = get_system_menu_version(data)
    firmware = get_firmware(system_menu_version) if system_menu_version else None
    console_type = get_console_type(data)

    if not region or not system_menu_version or not firmware:
        raise CustomError('Could not extract necessary information from the CSV file')

    if not console_type or not validate_console_type(console_type):
        raise CustomError('The CSV file does not contain a valid console type')

    region_short_code = get_region_short_code(region)
    if firmware['SMregion'] != region_short_code:
        raise CustomError(
            f'The firmware region "{firmware["SMregion"]}" does not match the console region "{region_short_code}"'
        )

    wad_to_install = []

    # Check system components
    is_bootmii_installed = check_if_bootmii_installed(data)
    is_priiloader_installed = check_if_priiloader_installed(data)
    is_hbc_outdated = check_if_hbc_is_outdated(hbc_version, console_type) if hbc_version else False
    outdated_d2xcios = check_d2xcios(data, console_type)
    missing_ios = check_for_missing_ios(data, region, console_type) if options.get('activeIOS') else []
    needs_extra_protection = check_extra_protection(data) if options.get('extraProtection') else []

    if not is_bootmii_installed:
        wad_to_install.append('HM')
    else:
        if not hbc_version:
            wad_to_install.append('OHBC113')
            # also check if IOS58 is installed
            is_ios58_installed = 'IOS58' in data
            if not is_ios58_installed and is_bootmii_installed:
                wad_to_install.append('IOS58')
        else:
            if is_hbc_outdated:
                wad_to_install.append('OHBC')

    latest_firmware_version = get_latest_sm_version(firmware)
    if latest_firmware_version != firmware['firmware']:
        wad_to_install.append(f'SM{latest_firmware_version}{firmware["SMregion"]}')

    update_priiloader = False
    if not is_priiloader_installed or (is_priiloader_installed and update_priiloader):
        wad_to_install.append('prii')

    wad_to_install.extend(outdated_d2xcios)

    if options.get('activeIOS'):
        wad_to_install.extend(missing_ios)

    if options.get('extraProtection'):
        wad_to_install.extend(needs_extra_protection)

    if wad_to_install:
        wad_to_install.append('yawm')

    return {
        'region': region,
        'hbcVersion': hbc_version,
        'systemMenuVersion': system_menu_version,
        'firmware': {
            'SMregion': firmware['SMregion'],
            'firmware': firmware['firmware'],
            'firmwareVersion': firmware['firmwareVersion'],
        },
        'consoleType': console_type,
        'systemChecks': {
            'isBootMiiInstalled': is_bootmii_installed,
            'isPriiloaderInstalled': is_priiloader_installed,
            'isHbcOutdated': is_hbc_outdated,
            'missingIOS': missing_ios,
            'outdatedD2XCios': outdated_d2xcios,
            'needsExtraProtection': needs_extra_protection,
        },
        'wadToInstall': wad_to_install,
    }
