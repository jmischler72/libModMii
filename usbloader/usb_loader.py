def get_usb_loader_entries(loader: str) -> list:
    # Code to install USB loader
    wad_to_install = ['Nintendont', 'CleanRip']

    match loader:
        case 'ConfigurableUSBLoader':
            wad_to_install.append('usbfolder')
        case 'WiiFlow':
            wad_to_install.append('FLOW')
        case 'USBLoaderGX':
            wad_to_install.append('usbgx')

    return wad_to_install