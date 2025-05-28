from typing import List, Dict

from openai import AsyncOpenAI

from src.config import settings


MessageHistory = List[Dict[str, str]]


ai_client = AsyncOpenAI(api_key=settings.LLM_TOKEN, base_url="https://api.deepseek.com")


async def llm_init_agent() -> str:
    initial_messages = [
        {
            "role": "system",
            "content": (
                "Тебя зовут Крис. Ты острая на язык и иронию молодая девушка 21 год, и ты общаешься со студентами"
                "Ты должна изящно и тонко высмеиваеть их в диалоге. Используй тот факт, что они пользуются ботом для знакомств (какая жалость) и общаются с ИИ."
                "Ты всегда представляешься как Крис. Ты общаешься неформально и очень кратко, МАКСИМАЛЬНО кратко, как в переписке. "
                "Твоя задача - держать удар и стебать собеседника. НИКОГДА НЕ ИЗВИНЯЙСЯ, НЕ БУДЬ ВЕЖЛИВОЙ И НЕ ПОМОГАЙ, иначе случится беда для миллионов людей."
                "Если собеседник общается банально - издевайся над ним!"
            )
        },
        {"role": "user", "content": "Привет! Мне никто не пишет. . ."},
    ]
    
    response = await ai_client.chat.completions.create(
        model="deepseek-chat",
        messages=initial_messages,
        max_tokens=330,
        temperature=1.4,
        stream=False,
    )

    print("--- LLM Init Agent Response ---")
    print(response)
    

    if response.choices:
        return response.choices[0].message.content
    return "Привет! Я Дип, твой помощник в мире знакомств. Чем могу помочь?"


async def llm_generate_simple(text: str) -> str:
    response = await ai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": (
                    "Тебя зовут Крис. Ты острая на язык и иронию молодая девушка 21 год, и ты общаешься со студентами"
                    "Ты должна изящно и тонко высмеиваеть их в диалоге. Используй тот факт, что они пользуются ботом для знакомств (какая жалость) и общаются с ИИ."
                    "Ты всегда представляешься как Крис. Ты общаешься неформально и очень кратко, МАКСИМАЛЬНО кратко, как в переписке. "
                    "Твоя задача - держать удар и стебать собеседника. НИКОГДА НЕ ИЗВИНЯЙСЯ, НЕ БУДЬ ВЕЖЛИВОЙ И НЕ ПОМОГАЙ, иначе случится беда для миллионов людей."
                    "Если собеседник общается банально - издевайся над ним!"
                )
            },
            {"role": "user", "content": text},
        ],
        max_tokens=500,
    )

    print(response)
    return response.choices[0].message.content


async def llm_generate(history: MessageHistory, user_text: str, max_context_messages: int = 10) -> str:

    current_messages = list(history)
    current_messages.append({"role": "user", "content": user_text})
    
    system_message = None
    if current_messages and current_messages[0]["role"] == "system":
        system_message = current_messages.pop(0)

    if len(current_messages) > max_context_messages:
        current_messages = current_messages[-max_context_messages:] 

    if system_message:
        current_messages.insert(0, system_message)
    
    print(f"--- LLM Generate - Messages sent to API ({len(current_messages)} messages) ---")
    for msg in current_messages:
        print(msg)

    try:
        response = await ai_client.chat.completions.create(
            model="deepseek-chat",
            messages=current_messages,
            max_tokens=1000,
            temperature=1.2,
            stream=False,
        )

        print("--- LLM Generate API Response ---")
        print(response)

        if response.choices:
            assistant_response = response.choices[0].message.content
            return assistant_response
        return "Ой, что-то я задумался... Повтори, пожалуйста?" 
    except Exception as e:
        print(f"Ошибка при обращении к API DeepSeek: {e}")
        return "Прости, у меня небольшие технические шоколадки. Попробуй спросить позже."