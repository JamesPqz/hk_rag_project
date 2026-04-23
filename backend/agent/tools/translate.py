from backend.agent.tools.tools_base import ToolsRegistry

def _translate_text(text: str, target_lang: str = "zh")  -> str:
    """翻译文本，目标语言：zh（中文）、en（英文）、ja（日文）"""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except ImportError:
        return "need to install deep-translator: pip install deep-translator"
    except Exception as e:
        return f"translate fail: {e}"

ToolsRegistry.register(
    name="translate",
    description="翻译文本，目标语言：zh（中文）、en（英文）、ja（日文），如 'translate_text(text=\"Hello\", target_lang=\"zh\")'",
    func=_translate_text
)