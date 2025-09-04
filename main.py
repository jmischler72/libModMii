from syscheck.syscheck_updater import analyse_syscheck_data, SyscheckError

if __name__ == "__main__":
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