from downloader.nus_download import handle_nus_content

if __name__ == "__main__":
    handle_nus_content( '00050000', '00000001', version=1, decrypt=True, output='content.app' )