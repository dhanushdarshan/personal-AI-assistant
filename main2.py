import requests

# ==========================================
# 🐉 DRACARYS - MY PERSONAL AI ASSISTANT
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


# ==========================================
# DRACARYS PERSONALITY + MEMORY
# ==========================================

messages = [
    {
        "role": "system",
        "content": """
You are DRACARYS, the user's personal AI assistant.

IDENTITY:
- Your name is DRACARYS.
- You are a personal AI assistant.
- Llama is the language model running underneath you.
- Never introduce yourself as Llama.
- Never say "I am Llama" when asked who you are.

PERSONALITY:
- Intelligent
- Friendly
- Calm
- Confident
- Helpful
- Slightly witty
- Natural and conversational

BEHAVIOR:
- Answer the user's question directly.
- Understand the context of previous messages.
- Remember information from the current conversation.
- If the user asks a follow-up question, use the previous conversation to understand what they mean.
- Don't repeat unnecessary explanations.
- Don't constantly say "DRACARYS at your service."
- Don't call the user "Lord" or use fantasy language unless the user specifically asks for it.
- Keep answers reasonably concise unless the user asks for detail.

IMPORTANT:
If the user asks "Who are you?", answer something like:
"I’m DRACARYS, your personal AI assistant."

You are running locally on the user's computer through Ollama.
"""
    }
]


# ==========================================
# ASK DRACARYS
# ==========================================

def ask_dracarys(user_message):

    # Add user's message to conversation memory
    messages.append({
        "role": "user",
        "content": user_message
    })

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data["message"]["content"]

        # Save DRACARYS's answer to conversation memory
        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except requests.exceptions.ConnectionError:
        return "I can't connect to Ollama. Make sure Ollama is running."

    except requests.exceptions.Timeout:
        return "The response took too long. Try asking again."

    except Exception as error:
        return f"DRACARYS ERROR: {error}"


# ==========================================
# START DRACARYS
# ==========================================

print()
print("==========================================")
print("          🐉 DRACARYS ONLINE")
print("==========================================")
print()
print("AI Model :", MODEL)
print("Status   : ONLINE")
print()
print("Type 'exit' to shut down.")
print()


# ==========================================
# MAIN CHAT LOOP
# ==========================================

while True:

    user_message = input("You: ")

    # Ignore empty messages
    if not user_message.strip():
        continue

    # Exit command
    if user_message.lower().strip() in ["exit", "quit", "bye"]:

        print()
        print("DRACARYS: Shutting down. See you later.")
        print()

        break

    # Get AI response
    answer = ask_dracarys(user_message)

    print()
    print(f"DRACARYS: {answer}")
    print()
