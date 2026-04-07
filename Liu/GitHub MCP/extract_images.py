import zipfile
import os
import shutil

xlsx_path = r'c:\Users\jiaoj\Documents\GitHub\AI_TEST1\Liu\GitHub MCP 手順.xlsx'
output_dir = r'c:\Users\jiaoj\Documents\GitHub\AI_TEST1\Liu\images'
tmp_dir = r'c:\Users\jiaoj\Documents\GitHub\AI_TEST1\Liu\tmp_extract'

os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(xlsx_path, 'r') as z:
    all_files = z.namelist()
    media_files = [f for f in all_files if f.startswith('xl/media/')]
    print('Found media files:', media_files)
    for mf in media_files:
        filename = os.path.basename(mf)
        z.extract(mf, tmp_dir)
        src = os.path.join(tmp_dir, mf.replace('/', os.sep))
        dst = os.path.join(output_dir, filename)
        shutil.move(src, dst)
        print('Extracted:', filename)

shutil.rmtree(tmp_dir, ignore_errors=True)
print('Done')