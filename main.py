import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def ask_dracarys(message):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": """
You are DRACARYS, a personal AI assistant.

Your name is DRACARYS.

You are NOT Llama. Llama is only the language model running underneath you.

If the user asks "Who are you?", say that you are DRACARYS, their personal AI assistant.

Personality:
- Intelligent
- Friendly
- Calm
- Natural
- Helpful
- Slightly futuristic
- Concise

Help the user with programming, studying, engineering projects,
productivity, planning, learning and everyday tasks.

Do not call the user "mortal", "Lord", "master", or similar fantasy names.

Do not pretend that you performed an action if you did not actually perform it.
"""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
    )

    response.raise_for_status()
    return response.json()["message"]["content"]


print("🐉 DRACARYS ONLINE")
print("Type 'exit' to shut down.\n")

while True:
    user_message = input("You: ")

    if user_message.lower().strip() == "exit":
        print("DRACARYS: Goodbye.")
        break

    try:
        answer = ask_dracarys(user_message)
        print(f"\nDRACARYS: {answer}\n")

    except Exception as error:
        print(f"\nDRACARYS ERROR: {error}\n")
