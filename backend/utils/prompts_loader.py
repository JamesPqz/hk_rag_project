from backend.utils.config_handler import prompts_config
from backend.utils.path_tool import get_abs_path
from backend.utils.logger_handler import logger


def _load_prompt(config_key: str, prompt_name: str) -> str:
    """通用提示词加载函数"""
    try:
        path = get_abs_path(prompts_config[config_key])
    except KeyError as e:
        logger.error(f'[{prompt_name}] missing config key: {config_key}')
        raise e

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f'[{prompt_name}] read file error: {str(e)}')
        raise e


def load_sys_prompt() -> str:
    return _load_prompt('main_prompt_path', 'load_sys_prompt')


def load_rag_summarize_prompt() -> str:
    return _load_prompt('rag_summarize_prompt_path', 'load_rag_prompt')


def load_report_prompt() -> str:
    return _load_prompt('report_prompt_path', 'load_report_prompt')

def load_intent_prompt() -> str:
    return _load_prompt('intent_prompt_path', 'load_report_prompt')

def load_react_system_prompt() -> str:
    return _load_prompt('react_system_prompt_path', 'load_react_system_prompt')

def load_boundaries() -> str:
    return _load_prompt('boundaries_path', 'load_boundaries')

def load_react_thought_prompt() -> str:
    return _load_prompt('react_thought_prompt_path', 'load_react_thought_prompt')


if __name__ == '__main__':
    print(load_rag_summarize_prompt())
    print(load_report_prompt())