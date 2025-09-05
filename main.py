from syscheck.syscheck_updater import analyse_syscheck_data, SyscheckError
from downloader.database import get_database_entry   
from downloader.download import download_entries

import asyncio

if __name__ == "__main__":
    
    print(get_database_entry("cIOS250[58]-v21") ) # Example usage of database function

    async def main():
        await download_entries(["EULAU"])  # Example usage of download function
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
        except SyscheckError as e:  
            print(f"Error: {e}")

    asyncio.run(main())