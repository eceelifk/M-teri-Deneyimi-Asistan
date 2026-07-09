chat_history = []


def add_to_memory(user_question, assistant_answer):
    chat_history.append({
        "user": user_question,
        "assistant": assistant_answer
    })

    if len(chat_history) > 5:
        chat_history.pop(0)


def get_memory_text():
    if not chat_history:
        return ""

    text = "Previous conversation:\n"

    for item in chat_history:
        text += f"User: {item['user']}\n"
        text += f"Assistant: {item['assistant']}\n\n"

    return text