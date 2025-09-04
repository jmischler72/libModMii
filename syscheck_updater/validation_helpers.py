latestd2xVersion = "10-beta52"  # Set this to the latest version as needed

def translate_keywords_to_english(csv_content: str) -> str:
    replacements = [
        ('Chaine Homebrew', 'Homebrew Channel'),
        ('Chaine Channel', 'Homebrew Channel'),
        ('Canale Homebrew', 'Homebrew Channel'),
        ('Canal Homebrew', 'Homebrew Channel'),
        ('Homebrewkanal', 'Homebrew Channel'),

        ('utilise', 'running on'),
        ("appoggiato all'", 'running on '),
        ('ejecutandose en', 'running on'),
        ('benutzt', 'running on'),

        ('Systemmenue', 'System Menu'),
        ('Menu Systeme', 'System Menu'),
        ('Menu di sistema', 'System Menu'),
        ('Menu de Sistema', 'System Menu'),

        ('Pas de patches', 'No Patches'),
        ('Non patchato', 'No Patches'),
        ('Sin Parches', 'No Patches'),
        ('Keine Patches', 'No Patches'),

        ('Bug Trucha', 'Trucha Bug'),

        ('Acces NAND', 'NAND Access'),
        ('Accesso NAND', 'NAND Access'),
        ('Acceso NAND', 'NAND Access'),
        ('NAND Zugriff', 'NAND Access'),

        ('Identificazione ES', 'ES Identify'),

        ('Type de Console', 'Console Type'),
        ('Tipo Console', 'Console Type'),
        ('Tipo de consola', 'Console Type'),
        ('Konsolentyp', 'Console Type'),

        ('Regione', 'Region'),

        ('original region', 'originally'),
        ("region d'origine", 'originally'),
        ('regione originale', 'originally'),
        ('region de origen', 'originally'),
    ]
    for pattern, replacement in replacements:
        csv_content = csv_content.replace(pattern, replacement)
    return csv_content

def validate_syscheck_data(data: str) -> bool:
    valid_syscheck_versions = [
        'SysCheck HDE',
        'SysCheck ME',
        'sysCheck v2.1.0b',
    ]
    return any(version in data for version in valid_syscheck_versions)

def validate_console_type(console_type: str) -> bool:
    return console_type in ["Wii", "vWii"]

def check_patched_vios80(data: str) -> bool:
    return bool(re.search(r'^vIOS80 \(rev \d+\):.*NAND Access', data, re.MULTILINE))

def check_d2x_cios(data: str, console_type: str) -> List[str]:
    cios_checks = [
        {'ios': 'cIOS248[38]-d2x-v10-beta52', 'pattern': r'^IOS248\[38\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'cIOS249[56]-d2x-v10-beta52', 'pattern': r'^IOS249\[56\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'cIOS250[57]-d2x-v10-beta52', 'pattern': r'^IOS250\[57\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'cIOS251[58]-d2x-v10-beta52', 'pattern': r'^IOS251\[58\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
    ]
    vios_checks = [
        {'ios': 'vIOS248[38]-d2x-v10-beta52', 'pattern': r'^vIOS248\[38\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'vIOS249[56]-d2x-v10-beta52', 'pattern': r'^vIOS249\[56\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'vIOS250[57]-d2x-v10-beta52', 'pattern': r'^vIOS250\[57\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
        {'ios': 'vIOS251[58]-d2x-v10-beta52', 'pattern': r'^vIOS251\[58\] \(rev \d+, Info:\s*d2x-v[^\)]*\)'},
    ]
    checks = cios_checks if console_type == "Wii" else vios_checks
    missing_ios = []
    for check in checks:
        match = re.search(check['pattern'], data, re.MULTILINE)
        if not match:
            missing_ios.append(check['ios'])
        else:
            version_match = re.search(r'd2x-v([^\)]*)', match.group(0))
            if not version_match:
                break
            installed_version = version_match.group(1)
            if installed_version != latestd2xVersion:
                # print(f"cIOS {check['ios']} is outdated: installed v{installed_version}, expected v{latestd2xVersion}")
                missing_ios.append(check['ios'])
    return missing_ios

def check_for_missing_ios(data: str, region: str, console_type: str) -> List[str]:
    active_ios_checks = [
        {'ios': 'IOS9', 'pattern': [re.compile(r'^IOS9 \(rev 1034\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS12', 'pattern': [re.compile(r'^IOS12 \(rev 526\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS13', 'pattern': [re.compile(r'^IOS13 \(rev 1032\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS14', 'pattern': [re.compile(r'^IOS14 \(rev 1032\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS15', 'pattern': [re.compile(r'^IOS15 \(rev 1032\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS17', 'pattern': [re.compile(r'^IOS17 \(rev 1032\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS21', 'pattern': [re.compile(r'^IOS21 \(rev 1039\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS22', 'pattern': [re.compile(r'^IOS22 \(rev 1294\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS28', 'pattern': [re.compile(r'^IOS28 \(rev 1807\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS31', 'pattern': [re.compile(r'^IOS31 \(rev 3608\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS33', 'pattern': [re.compile(r'^IOS33 \(rev 3608\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS34', 'pattern': [re.compile(r'^IOS34 \(rev 3608\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS35', 'pattern': [re.compile(r'^IOS35 \(rev 3608\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS36', 'pattern': [re.compile(r'^IOS36 \(rev 3608\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS37', 'pattern': [re.compile(r'^IOS37 \(rev 5663\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS38', 'pattern': [re.compile(r'^IOS38 \(rev 4124\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS41', 'pattern': [re.compile(r'^IOS41 \(rev 3607\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS43', 'pattern': [re.compile(r'^IOS43 \(rev 3607\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS45', 'pattern': [re.compile(r'^IOS45 \(rev 3607\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS46', 'pattern': [re.compile(r'^IOS46 \(rev 3607\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS48', 'pattern': [re.compile(r'^IOS48 \(rev 4124\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS53', 'pattern': [re.compile(r'^IOS53 \(rev 5663\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS55', 'pattern': [re.compile(r'^IOS55 \(rev 5663\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS56', 'pattern': [re.compile(r'^IOS56 \(rev 5662\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS57', 'pattern': [re.compile(r'^IOS57 \(rev 5919\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS61', 'pattern': [re.compile(r'^IOS61 \(rev 5662\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS62', 'pattern': [re.compile(r'^IOS62 \(rev 6430\): No Patches$', re.MULTILINE)]},
        {'ios': 'IOS58', 'pattern': [
            re.compile(r'^IOS58 \(rev 6176\): No Patches$', re.MULTILINE),
            re.compile(r'^IOS58 \(rev 6176\): USB 2\.0$', re.MULTILINE)
        ]},
        {'ios': 'BC', 'pattern': [re.compile(r'^BC v6$', re.MULTILINE)]},
        {'ios': 'IOS59', 'pattern': [re.compile(r'^IOS59 \(rev 9249\): No Patches$', re.MULTILINE)], 'condition': region.upper() == "J"}
    ]
    vactive_ios_checks = [
        {'ios': 'vIOS9', 'pattern': [re.compile(r'^vIOS9 \(rev 1290\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS12', 'pattern': [re.compile(r'^vIOS12 \(rev 782\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS13', 'pattern': [re.compile(r'^vIOS13 \(rev 1288\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS14', 'pattern': [re.compile(r'^vIOS14 \(rev 1288\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS15', 'pattern': [re.compile(r'^vIOS15 \(rev 1288\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS17', 'pattern': [re.compile(r'^vIOS17 \(rev 1288\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS21', 'pattern': [re.compile(r'^vIOS21 \(rev 1295\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS22', 'pattern': [re.compile(r'^vIOS22 \(rev 1550\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS28', 'pattern': [re.compile(r'^vIOS28 \(rev 2063\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS31', 'pattern': [re.compile(r'^vIOS31 \(rev 3864\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS33', 'pattern': [re.compile(r'^vIOS33 \(rev 3864\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS34', 'pattern': [re.compile(r'^vIOS34 \(rev 3864\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS35', 'pattern': [re.compile(r'^vIOS35 \(rev 3864\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS36', 'pattern': [re.compile(r'^vIOS36 \(rev 3864\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS37', 'pattern': [re.compile(r'^vIOS37 \(rev 5919\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS38', 'pattern': [re.compile(r'^vIOS38 \(rev 4380\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS41', 'pattern': [re.compile(r'^vIOS41 \(rev 3863\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS43', 'pattern': [re.compile(r'^vIOS43 \(rev 3863\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS45', 'pattern': [re.compile(r'^vIOS45 \(rev 3863\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS46', 'pattern': [re.compile(r'^vIOS46 \(rev 3863\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS48', 'pattern': [re.compile(r'^vIOS48 \(rev 4380\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS53', 'pattern': [re.compile(r'^vIOS53 \(rev 5919\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS55', 'pattern': [re.compile(r'^vIOS55 \(rev 5919\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS56', 'pattern': [re.compile(r'^vIOS56 \(rev 5918\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS57', 'pattern': [re.compile(r'^vIOS57 \(rev 6175\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS59', 'pattern': [re.compile(r'^vIOS59 \(rev 9249\): No Patches$', re.MULTILINE)]},
        {'ios': 'vIOS61', 'pattern': [re.compile(r'^vIOS61 \(rev 5918\)', re.MULTILINE)]},
        {'ios': 'vIOS62', 'pattern': [re.compile(r'^vIOS62 \(rev 6942\): No Patches$', re.MULTILINE)]},
        {'ios': 'BCnand', 'pattern': [re.compile(r'^vIOS512 \(rev 7\): No Patches$', re.MULTILINE)]},
        {'ios': 'BCwfs', 'pattern': [re.compile(r'^vIOS513 \(rev 1\): No Patches$', re.MULTILINE)]},
    ]
    checks = active_ios_checks if console_type == "Wii" else vactive_ios_checks
    missing_ios = []
    for check in checks:
        if 'condition' in check and not check['condition']:
            continue
        patterns = check['pattern']
        if not any(pattern.search(data) for pattern in patterns):
            missing_ios.append(check['ios'])
    return missing_ios


def check_extra_protection(data: str) -> list:
    extra_protection_checks = [
        {
            'ios': 'IOS11P60',
            'patterns': [
                re.compile(r'^IOS11 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS11 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS11\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS20P60',
            'patterns': [
                re.compile(r'^IOS20 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS20 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS20\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS30P60',
            'patterns': [
                re.compile(r'^IOS30 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS30 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS30\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS40P60',
            'patterns': [
                re.compile(r'^IOS40 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS40 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS40\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS50P',
            'patterns': [
                re.compile(r'^IOS50 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS50 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS50\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS52P',
            'patterns': [
                re.compile(r'^IOS52 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS52 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS52\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS60P',
            'patterns': [
                re.compile(r'^IOS60 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS60 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS60 \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS70K',
            'patterns': [
                re.compile(r'^IOS70 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS70 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS70\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        },
        {
            'ios': 'IOS80K',
            'patterns': [
                re.compile(r'^IOS80 \(rev 16174\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS80 \(rev 65535\): Trucha Bug, NAND Access$', re.MULTILINE),
                re.compile(r'^IOS80\[60\] \(rev \d+, Info: ModMii-IOS60-v6174\)$', re.MULTILINE)
            ]
        }
    ]
    missing_extra_protection = []
    for check in extra_protection_checks:
        has_protection = any(pattern.search(data) for pattern in check['patterns'])
        if not has_protection:
            missing_extra_protection.append(check['ios'])
    return missing_extra_protection

def check_if_hbc_is_outdated(hbc_version: str, console_type: str) -> bool:
    required_version = "1.1.2" if console_type == "Wii" else "1.1.3"
    hbc_parts = [int(x) for x in hbc_version.split('.')]
    req_parts = [int(x) for x in required_version.split('.')]
    # Compare version numbers
    for hbc, req in zip(hbc_parts, req_parts):
        if hbc > req:
            return False
        elif hbc < req:
            return True
    return len(hbc_parts) < len(req_parts)

def check_if_bootmii_installed(data: str) -> bool:
    return 'BootMii' in data

def check_if_priiloader_installed(data: str) -> bool:
    return 'Priiloader' in data
