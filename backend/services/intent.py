from backend.api.chat import llm_service
from backend.utils.prompts_loader import load_intent_prompt


def classify_intent(query: str) -> str:
    template = load_intent_prompt()
    prompt = template.format(query=query)
    response = llm_service.generate(prompt)
    intent = response.strip().upper()

    if intent not in ["TOOL", "KNOWLEDGE", "CHAT", "OTHER"]:
        return "OTHER"

    return intent

if __name__ == '__main__':
    print(classify_intent('Thank you'))
    print(classify_intent('金管局是什么'))
    print(classify_intent("what's the weather like tomorrow"))
    print(classify_intent('la la la la la la'))