import zipfile
import os

xlsx_path = r'GitHub MCP 手順.xlsx'

with zipfile.ZipFile(xlsx_path, 'r') as z:
    items = z.namelist()
    with open('xlsx_contents.txt', 'w', encoding='utf-8') as f:
        for item in items:
            f.write(item + '\n')
            print(item)

print('Total files:', len(items))