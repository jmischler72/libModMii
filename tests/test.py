
from libModMii.database.database import get_database_entry
from libModMii.syscheck.syscheck_updater import analyse_syscheck_data, SyscheckError
from libModMii.download import download_entries
from libModMii.usbloader.usb_loader import get_usb_loader_entries



def test_database():
    entry = get_database_entry("cIOS250[58]-v21")
    print("Database Entry:", entry)

def test_syscheck():
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
    except SyscheckError as e:
        print(f"Syscheck Error: {e}")

def test_usbloader():
    usb_loader_entries = get_usb_loader_entries('USBLoaderGX')
    print("USB Loader Entries:", usb_loader_entries)
    # Example: download_entry for each loader entry
    for entry in usb_loader_entries:
        print(f"Downloading USB loader entry: {entry}")
        # download_entry(entry)  # Uncomment to actually download

if __name__ == "__main__":
    test_database()
    test_syscheck()
    test_usbloader()
