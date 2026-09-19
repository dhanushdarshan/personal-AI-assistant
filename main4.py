import requests
import json
import os
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import numpy as np
from datetime import datetime


# ============================================================
# 🐉 DRACARYS - PERSONAL AI ASSISTANT
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"
MEMORY_FILE = "memory.json"


# ============================================================
# 🔊 VOICE OUTPUT
# ============================================================

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):
    print()
    print("DRACARYS:", text)
    print()

    engine.say(text)
    engine.runAndWait()


# ============================================================
# 🎤 MICROPHONE
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5


def listen():

    print()
    print("🎤 DRACARYS IS LISTENING...")
    print("👉 Speak now!")

    try:

        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16"
        )

        sd.wait()

        print("🧠 Processing your voice...")

        audio_bytes = recording.tobytes()

        audio_data = sr.AudioData(
            audio_bytes,
            SAMPLE_RATE,
            2
        )

        recognizer = sr.Recognizer()

        text = recognizer.recognize_google(
            audio_data
        )

        print()
        print("YOU SAID:", text)
        print()

        return text

    except Exception as error:

        print()
        print("❌ MICROPHONE ERROR:")
        print(error)
        print()

        return ""


# ============================================================
# 🧠 MEMORY
# ============================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return []


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False
        )


memory = load_memory()


def remember(text):

    memory.append(
        {
            "memory": text,
            "saved_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
    )

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

        memory_text = "\n\nPERSONAL MEMORY:\n"

        for item in memory:

            memory_text += (
                "- "
                + item["memory"]
                + "\n"
            )

    else:

        memory_text = (
            "\n\nPERSONAL MEMORY:\n"
            "No memories saved yet.\n"
        )

    return f"""
You are DRACARYS, Dhanush's personal AI assistant.

Your name is DRACARYS.

You are NOT Llama.
Llama is only the language model running underneath you.

If Dhanush asks who you are, say:
"I am DRACARYS, your personal AI assistant."

PERSONALITY:

- Intelligent
- Friendly
- Helpful
- Calm
- Slightly witty
- Natural
- Concise

You are being developed as a personal assistant.

Use the personal memory below when relevant.

{memory_text}
"""


# ============================================================
# 💬 TALK TO OLLAMA
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
print("==========================================")
print("🐉 DRACARYS ONLINE")
print("==========================================")
print()

print(
    "🧠 Memories loaded:",
    len(memory)
)

print()
print("Press ENTER to speak.")
print("Type a message to use keyboard.")
print()
print("Commands:")
print("remember <something>")
print("memory")
print("forget")
print("exit")
print()


# ============================================================
# 🔄 MAIN LOOP
# ============================================================

while True:

    try:

        user_input = input(
            "You (ENTER = voice): "
        ).strip()


        # ----------------------------------------------------
        # 🎤 VOICE
        # ----------------------------------------------------

        if user_input == "":

            user_message = listen()

            if not user_message:

                continue

        else:

            user_message = user_input


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_message.lower() == "exit":

            speak(
                "Goodbye, Dhanush."
            )

            break


        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

        if user_message.lower().startswith(
            "remember "
        ):

            fact = user_message[9:].strip()

            if fact:

                remember(fact)

                speak(
                    "Got it. I'll remember that."
                )

            continue


        # ----------------------------------------------------
        # SHOW MEMORY
        # ----------------------------------------------------

        if user_message.lower() == "memory":

            if not memory:

                speak(
                    "I don't have any saved memories yet."
                )

            else:

                result = "Here's what I remember. "

                for number, item in enumerate(
                    memory,
                    start=1
                ):

                    result += (
                        f"{number}. "
                        f"{item['memory']}. "
                    )

                speak(result)

            continue


        # ----------------------------------------------------
        # FORGET
        # ----------------------------------------------------

        if user_message.lower() == "forget":

            confirmation = input(
                "Type YES to delete all memory: "
            ).strip()

            if confirmation == "YES":

                forget_all_memory()

                speak(
                    "All permanent memories have been deleted."
                )

            else:

                speak(
                    "Okay, I kept your memories."
                )

            continue


        # ----------------------------------------------------
        # 🧠 AI
        # ----------------------------------------------------

        try:

            answer = ask_dracarys(
                user_message
            )

            speak(answer)

        except requests.exceptions.ConnectionError:

            speak(
                "Ollama is not running. Please start Ollama first."
            )

        except Exception as error:

            print()
            print("DRACARYS ERROR:", error)
            print()

            speak(
                "Something went wrong."
            )


    except KeyboardInterrupt:

        print()

        speak(
            "Shutting down safely."
        )

        break
