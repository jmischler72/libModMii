from syscheck.syscheck_updater import analyse_syscheck_data, SyscheckError
from downloader.database import get_database_entry   
from downloader.download import download_entries
from usbloader.usb_loader import get_usb_loader_entries


if __name__ == "__main__":
    print(get_database_entry("cIOS250[58]-v21") ) # Example usage of database function

    with open('test-syscheck.csv', 'r', encoding='utf-8') as file:
        copy_data = file.read()

    try:
        result = analyse_syscheck_data(
            copy_data,
            activeIOS=True,
            extraProtection=True,
            cMios=False
        )
        print("Analysis Result:", result)
        print("WADs to Install:", result.get("wadToInstall"))
        
        #download_entries(result.get("wadToInstall"))  # Example usage of download function
        

        usb_loader_entries = get_usb_loader_entries('USBLoaderGX')
        print("USB Loader Entries:", usb_loader_entries)
        
        download_entries(usb_loader_entries)  # Example usage of download function for USB loaders
        
    except SyscheckError as e:
        print(f"Error: {e}")
