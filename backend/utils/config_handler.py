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
    with open(get_abs_path(cfg_path), encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

rag_config = load_config('config/rag.yml')
chroma_config = load_config('config/chroma.yml')
prompts_config = load_config('config/prompts.yml')
agent_config = load_config('config/agent.yml')
postgresql_config = load_config('config/pgvector.yml')
redis_config = load_config('config/redis.yml')
vector_config = load_config('config/vector.yml')

if __name__ == '__main__':
    print(postgresql_config['pg_user'])