import csv, collections, os, json, sys

path = 'myDeductionExpenses.csv'
CONFIG_FILE = 'config.json'

if len(sys.argv) > 1:
    path = sys.argv[1]
elif os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            path = cfg.get('files', {}).get('base_expense_file', path)
    except Exception:
        pass

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)
duplicates = collections.defaultdict(list)
with open(path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        key = tuple(row)
        duplicates[key].append(i)

found = False
for key, lines in duplicates.items():
    if len(lines) > 1:
        found = True
        print('Duplicate rows at lines:', lines)
        print('Row content:', ','.join(key))
if not found:
    print('No duplicate rows found')
