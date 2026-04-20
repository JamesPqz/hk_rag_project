import os
import re

import yaml
from backend.utils.path_tool import get_abs_path

# def load_rag_config(cfg_path = get_abs_path('config/rag.yml'), encoding = 'utf-8'):
#     with open(cfg_path, encoding=encoding) as f:
#         return yaml.load(f, Loader=yaml.FullLoader)
#
# def load_chroma_config(cfg_path = get_abs_path('config/chroma.yml'), encoding = 'utf-8'):
#     with open(cfg_path, encoding=encoding) as f:
#         return yaml.load(f, Loader=yaml.FullLoader)
#
# def load_prompts_config(cfg_path = get_abs_path('config/prompts.yml'), encoding = 'utf-8'):
#     with open(cfg_path, encoding=encoding) as f:
#         return yaml.load(f, Loader=yaml.FullLoader)
#
# def load_agent_config(cfg_path = get_abs_path('config/agent.yml'), encoding = 'utf-8'):
#     with open(cfg_path, encoding=encoding) as f:
#         return yaml.load(f, Loader=yaml.FullLoader)

def load_config(cfg_path:str, encoding='utf-8'):
    # print(get_abs_path(cfg_path))
    # with open(get_abs_path(cfg_path), encoding=encoding) as f:
    #     return yaml.load(f, Loader=yaml.FullLoader)
    with open(get_abs_path(cfg_path), encoding=encoding) as f:
        content = f.read()

    # 核心修复：支持 ${VAR:-default} 格式的环境变量替换
    def replace_env(match):
        expr = match.group(1)
        # 拆分变量名和默认值（匹配 :- 分隔）
        if ':-' in expr:
            var_name, default_val = expr.split(':-', 1)
            return os.getenv(var_name, default_val)
        # 普通 ${VAR} 格式
        else:
            return os.getenv(expr, match.group(0))

    # 正则匹配所有 ${...} 格式
    content = re.sub(r'\$\{([^}]+)\}', replace_env, content)

    return yaml.safe_load(content)

rag_config = load_config('config/rag.yml')
chroma_config = load_config('config/chroma.yml')
prompts_config = load_config('config/prompts.yml')
agent_config = load_config('config/agent.yml')
postgresql_config = load_config('config/pgvector.yml')
redis_config = load_config('config/redis.yml')
vector_config = load_config('config/vector.yml')

if __name__ == '__main__':
    print(postgresql_config['pg_user'])