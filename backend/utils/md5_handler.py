import os.path

from backend.utils.path_tool import get_abs_path
from backend.utils.config_handler import chroma_config as cfg

def check_md5_hex(md5_for_check:str):
    md5_path = get_abs_path(cfg['md5_hex_store'])
    if not os.path.exists(md5_path):
        open(md5_path, 'w', encoding='utf-8').close()
        return False
    with open(md5_path,'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line == md5_for_check:
                return True

    return False

def save_md5(md5:str):
    md5_path = get_abs_path(cfg['md5_hex_store'])
    with open(md5_path, 'a', encoding='utf-8') as f:
        f.write(md5 + '\n')

def clear_md5_records():
    md5_path = get_abs_path(cfg['md5_hex_store'])
    if os.path.exists(md5_path):
        with open(md5_path, 'w') as f:
            f.write('')