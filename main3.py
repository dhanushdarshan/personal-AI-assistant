import requests
import json
import os
from datetime import datetime

# ============================================================
# 🐉 DRACARYS - MY PERSONAL AI ASSISTANT
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

MEMORY_FILE = "memory.json"


# ============================================================
# 🧠 PERMANENT MEMORY
# ============================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


memory = load_memory()


def remember(text):
    memory.append({
        "memory": text,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_memory(memory)


def forget_all_memory():
    global memory

    memory = []
    save_memory(memory)


# ============================================================
# 🤖 DRACARYS PERSONALITY
# ============================================================

def build_system_prompt():

    memory_text = ""

    if memory:
        memory_text = "\n\nIMPORTANT PERSONAL MEMORY:\n"

        for item in memory:
            memory_text += "- " + item["memory"] + "\n"

    else:
        memory_text = "\n\nIMPORTANT PERSONAL MEMORY:\nNo saved memories yet.\n"

    return f"""
You are DRACARYS, the user's personal AI assistant.

IDENTITY:
- Your name is DRACARYS.
- You are a personal AI assistant.
- Llama is the language model running underneath you.
- Never introduce yourself as Llama.
- If the user asks "Who are you?", say you are DRACARYS, their personal AI assistant.

PERSONALITY:
- Intelligent
- Helpful
- Calm
- Friendly
- Slightly witty
- Speak naturally like a personal assistant.
- Keep answers useful and understandable.
- Do not constantly mention that you are an AI.

MEMORY:
You have access to the user's permanent memory below.
Use it naturally when relevant.
Do not claim to remember something unless it appears in the memory.

{memory_text}
"""


# ============================================================
# 💬 ASK DRACARYS
# ============================================================

def ask_dracarys(user_message):

    messages = [
        {
            "role": "system",
            "content": build_system_prompt()
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "stream": False,
            "messages": messages
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


# ============================================================
# 🐉 START DRACARYS
# ============================================================

print()
print("========================================")
print("🐉 DRACARYS ONLINE")
print("========================================")
print()

if memory:
    print(f"🧠 Permanent memories loaded: {len(memory)}")
else:
    print("🧠 No permanent memories yet.")

print()
print("Commands:")
print("  remember <something>  → Save something permanently")
print("  memory                → Show saved memories")
print("  forget                → Delete all saved memories")
print("  exit                  → Shut down DRACARYS")
print()


# ============================================================
# 🔄 MAIN LOOP
# ============================================================

while True:

    try:
        user_message = input("You: ").strip()

        if not user_message:
            continue


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_message.lower() == "exit":

            print()
            print("DRACARYS: Goodbye, Dhanush. 🐉")
            print()

            break


        # ----------------------------------------------------
        # REMEMBER
        # ----------------------------------------------------

        if user_message.lower().startswith("remember "):

            fact = user_message[9:].strip()

            if fact:

                remember(fact)

                print()
                print("DRACARYS: 🧠 Got it. I'll remember that.")
                print()

            continue


        # ----------------------------------------------------
        # SHOW MEMORY
        # ----------------------------------------------------

        if user_message.lower() == "memory":

            print()

            if not memory:

                print("DRACARYS: 🧠 I don't have any permanent memories yet.")

            else:

                print("DRACARYS: 🧠 Here's what I remember:")

                for number, item in enumerate(memory, start=1):

                    print(f"{number}. {item['memory']}")

            print()

            continue


        # ----------------------------------------------------
        # DELETE MEMORY
        # ----------------------------------------------------

        if user_message.lower() == "forget":

            confirmation = input(
                "DRACARYS: This will delete ALL permanent memories. Type YES to confirm: "
            ).strip()

            if confirmation == "YES":

                forget_all_memory()

                print()
                print("DRACARYS: 🧠 All permanent memories have been deleted.")
                print()

            else:

                print()
                print("DRACARYS: Memory deletion cancelled.")
                print()

            continue


        # ----------------------------------------------------
        # NORMAL AI CHAT
        # ----------------------------------------------------

        try:

            answer = ask_dracarys(user_message)

            print()
            print("DRACARYS:", answer)
            print()

        except requests.exceptions.ConnectionError:

            print()
            print("DRACARYS ERROR: Ollama is not running.")
            print("Please start Ollama and try again.")
            print()

        except Exception as error:

            print()
            print("DRACARYS ERROR:", error)
            print()


    except KeyboardInterrupt:

        print()
        print()
        print("DRACARYS: Shutting down safely. 🐉")
        print()

        break
