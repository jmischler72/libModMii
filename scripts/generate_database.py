import os
import re
import requests
import json
from datetime import datetime

# Download DB.bat from URL
download_url = 'https://raw.githubusercontent.com/modmii/modmii.github.io/refs/heads/master/Support/subscripts/DB.bat'
db_file_path = os.path.join(os.path.dirname(__file__), 'DB.bat')

print('Downloading DB.bat...')

response = requests.get(download_url)
if response.status_code == 200:
  with open(db_file_path, 'w', encoding='utf-8') as f:
    f.write(response.text)
  print('Download completed!')
else:
  print('Download failed:', response.status_code)
  exit(1)

def evaluate_variables(entry):
  """
  Evaluates and replaces variable placeholders in the values of a dictionary.

  Iteratively searches for string values in the given dictionary `entry` that contain
  variable placeholders in the format `%VAR_NAME%`. For each placeholder found, it replaces
  it with the corresponding value from the dictionary. The process repeats until no more
  replacements are made or a maximum number of iterations is reached to prevent infinite loops.

  Args:
    entry (dict): The dictionary containing key-value pairs where values may include
            variable placeholders.

  Returns:
    None: The function modifies the input dictionary in place.
  """
  changed = True
  iterations = 0
  max_iterations = 10
  while changed and iterations < max_iterations:
    changed = False
    iterations += 1
    for key in entry:
      value = entry[key]
      if isinstance(value, str) and '%' in value:
        original_value = value
        def repl(match):
          var_name = match.group(1)
          return str(entry.get(var_name, match.group(0)))
        value = re.sub(r'%([^%]+)%', repl, value)
        if value != original_value:
          entry[key] = value
          changed = True

def categorize_entry(entry_id, entry):
  """
  Categorizes a given entry dictionary by adding a 'category' key based on its properties.

  Parameters:
    entry_id (str): The identifier for the entry.
    entry (dict): The entry to categorize. May contain keys such as 'name', 'ciosslot', 'ciosversion',
            'cIOSFamilyName', 'basecios', and 'diffpath'.

  Behavior:
    - If the entry already contains a 'category' key, no action is taken.
    - If the entry's 'name' or entry_id contains 'd2x' (case-insensitive), sets entry['category'] to 'd2x'.
    - If the entry's 'name' or entry_id contains 'cios' (case-insensitive), or if any of the following keys
      are present and truthy in the entry: 'ciosslot', 'ciosversion', 'cIOSFamilyName', 'basecios', 'diffpath',
      sets entry['category'] to 'cios'.
  """
  if 'category' in entry:
    return
  name = entry.get('name', '')
  entry_id_lower = entry_id.lower()
  name_lower = name.lower()
  if 'd2x' in name_lower or 'd2x' in entry_id_lower:
    entry['category'] = 'd2x'
    return
  if (
    'cios' in name_lower or
    'cios' in entry_id_lower or
    entry.get('ciosslot') or
    entry.get('ciosversion') or
    entry.get('cIOSFamilyName') or
    entry.get('basecios') or
    entry.get('diffpath')
  ):
    entry['category'] = 'cios'
    return

def process_db_file():
  """
  Parses a batch database file, extracts structured entries, and converts them to a JSON format.

  The function reads the batch file specified by `db_file_path`, processes its contents line by line,
  and constructs a dictionary containing metadata and entries. It filters out irrelevant lines, identifies
  entry labels, and extracts key-value pairs from 'set' commands within each entry. Entries are further
  evaluated and categorized using helper functions `evaluate_variables` and `categorize_entry`.
  Invalid or empty entries are removed before saving the final result.

  The output JSON is written to '../database/database.json' relative to the script's location.
  The function prints a summary upon completion.

  Side Effects:
    - Writes the converted JSON data to a file.
    - Prints conversion status and entry count to stdout.

  Dependencies:
    - Assumes existence of `db_file_path`, `evaluate_variables`, and `categorize_entry`.
    - Uses `os`, `json`, `re`, and `datetime` modules.

  Returns:
    None
  """
  with open(db_file_path, 'r', encoding='utf-8') as f:
    batch_content = f.read()
  lines = [line.strip() for line in batch_content.split('\n') if line.strip()]
  result = {
    'meta': {
      'DBversion': None,
      'converted': datetime.utcnow().isoformat() + 'Z',
      'source': 'DB.bat',
      'creator': "https://github.com/xflak",
    },
    'entries': {}
  }
  current_entry = None
  in_entry = False
  for line in lines:
    if line.startswith('set DBversion='):
      result['meta']['DBversion'] = line.split('=', 1)[1]
      continue
    if (
      'goto:' in line or
      'if ' in line or
      'call ' in line or
      'move ' in line or
      'exist ' in line or
      line.startswith('::') or
      'cls' in line or
      'echo' in line
    ):
      continue
    if line.startswith(':'):
      label = line[1:]
      if (
        label in ['skip', 'DBend'] or
        ' ' in label or
        ':' in label or
        'Rename' in label or
        'download' in label
      ):
        in_entry = False
        continue
      current_entry = label
      in_entry = True
      result['entries'][current_entry] = {}
      continue
    if in_entry and current_entry and line.startswith('set '):
      set_command = line[4:]
      if set_command.startswith('"') and '=' in set_command and set_command.endswith('"'):
        set_command = set_command[1:-1]
      equal_index = set_command.find('=')
      if equal_index != -1:
        key = set_command[:equal_index]
        value = set_command[equal_index + 1:]
        value = re.sub(r'^"|"$', '', value)
        if re.fullmatch(r'[0-9A-Fa-f]+', value) and len(value) > 4:
          pass
        elif value.isdigit():
          value = int(value)
        result['entries'][current_entry][key] = value
  to_delete = []
  for entry_key, entry in result['entries'].items():
    evaluate_variables(entry)
    categorize_entry(entry_key, entry)
    if not entry or (len(entry) == 1 and entry.get('name') is None):
      to_delete.append(entry_key)
  for key in to_delete:
    del result['entries'][key]
  output_file_path = os.path.join(os.path.dirname(__file__), '../database/database.json')
  os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
  with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
  print('Conversion completed! Output written to public/database.json')
  print(f'Converted {len(result["entries"])} entries')

process_db_file()
