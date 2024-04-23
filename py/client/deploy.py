from pathlib import Path

import zipfile


with zipfile.ZipFile("client.zip", mode="w")as zf:
    for path in tuple(Path('assets').rglob('*'))+('client_main.exe',):
        zf.write(path, path, compress_type=zipfile.ZIP_DEFLATED)
