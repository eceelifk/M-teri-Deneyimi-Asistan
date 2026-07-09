from app.llm import ask_llm


def clean_model_output(text):
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return text.strip().strip('"')


def en_to_tr(text):
    prompt = f"""
Translate the following English text into Turkish.
Do not explain.
Do not show reasoning.
Do not use <think>.
Only return the Turkish translation.

TEXT:
{text}
"""
    return clean_model_output(ask_llm(prompt))