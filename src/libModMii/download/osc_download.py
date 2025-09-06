import os
import requests

OSC_URL = 'https://hbb1.oscwii.org/api/contents/'

def osc_download(database_entry, file_path):
    try:
        file_url = f"{OSC_URL}{database_entry.code1}/{database_entry.code1}.zip"
        print(f"Downloading {database_entry.wadname} from {file_url}...")

        response = requests.get(file_url)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            f.write(response.content)
        print('OSC download process completed')
    except Exception as error:
        print('OSC download failed:', error)
        raise
