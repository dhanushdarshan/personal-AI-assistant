import requests
import json
import os
import subprocess
import speech_recognition as sr
from datetime import datetime


# ============================================================
# 🐉 DRACARYS - MY PERSONAL AI ASSISTANT
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"
MEMORY_FILE = "memory.json"


# ============================================================
# 🧠 MEMORY SYSTEM
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

    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=4, ensure_ascii=False)

    except Exception as error:
        print("Memory save error:", error)


memory = load_memory()


# ============================================================
# 🔊 TEXT TO SPEECH
# ============================================================

def speak(text):

    if not text:
        return

    print()
    print("🐉 DRACARYS:", text)
    print()

    try:

        # Protect text for PowerShell
        safe_text = text.replace("'", "''")

        powershell_command = f"""
Add-Type -AssemblyName System.Speech

$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer

$voice.Volume = 100
$voice.Rate = 0

$voice.Speak('{safe_text}')

$voice.Dispose()
"""

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_command
            ],
            check=True
        )

    except Exception as error:

        print("🔊 VOICE ERROR:", error)


# ============================================================
# 🎤 VOICE INPUT
# ============================================================

recognizer = sr.Recognizer()


def listen():

    microphone = sr.Microphone()

    with microphone as source:

        print()
        print("🎤 DRACARYS IS LISTENING...")
        print("👉 Speak now!")

        try:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=20
            )

        except sr.WaitTimeoutError:

            print("⏱️ I didn't hear anything.")

            return ""

    print("🧠 Processing your voice...")

    try:

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print()
        print("YOU SAID:", text)
        print()

        return text

    except sr.UnknownValueError:

        print("❌ I couldn't understand that.")

        speak("Sorry, I couldn't understand you.")

        return ""

    except sr.RequestError as error:

        print("❌ Speech recognition error:", error)

        speak("I'm having trouble connecting to speech recognition.")

        return ""

    except Exception as error:

        print("❌ Microphone error:", error)

        return ""


# ============================================================
# 🧠 DRACARYS PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are DRACARYS, Dhanush's personal AI assistant.

IDENTITY:
- Your name is DRACARYS.
- You are a personal AI assistant.
- Llama is only the language model running underneath you.
- Never introduce yourself as Llama.
- If asked "Who are you?", say that you are DRACARYS.
- The user is Dhanush.

PERSONALITY:
- Intelligent
- Friendly
- Calm
- Slightly witty
- Helpful
- Confident
- Natural
- Speak like a personal assistant, not like a robotic chatbot.

IMPORTANT:
- Keep normal spoken answers reasonably short.
- Do not produce huge paragraphs unless the user asks for detail.
- Since your answers will be spoken aloud, prefer natural sentences.
- Do not use excessive markdown.
- Do not use tables unless specifically requested.
- Answer directly.

Dhanush is building you as his personal AI assistant.
Help him with programming, engineering, projects, studying,
productivity, planning, and everyday questions.

Current date:
"""


# ============================================================
# 💬 ASK OLLAMA
# ============================================================

conversation = []


def ask_dracarys(user_message):

    global conversation

    current_date = datetime.now().strftime("%d %B %Y")

    system_message = SYSTEM_PROMPT + current_date

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    # Add saved memories
    if memory:

        memory_text = "\n".join(
            f"- {item}"
            for item in memory
        )

        messages.append(
            {
                "role": "system",
                "content": (
                    "Permanent memories about Dhanush:\n"
                    + memory_text
                )
            }
        )

    # Add conversation history
    messages.extend(conversation[-12:])

    # Add current message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

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

        answer = data["message"]["content"].strip()

        # Save conversation
        conversation.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "I can't connect to Ollama right now. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "The AI took too long to respond."
        )

    except Exception as error:

        print()
        print("OLLAMA ERROR:", error)
        print()

        return (
            "Something went wrong while processing that."
        )


# ============================================================
# 🧠 MEMORY COMMANDS
# ============================================================

def handle_memory_command(command):

    global memory

    lower_command = command.lower().strip()

    # Remember
    if lower_command.startswith("remember "):

        new_memory = command[9:].strip()

        if not new_memory:

            speak("Tell me what you want me to remember.")

            return True

        memory.append(new_memory)

        save_memory(memory)

        speak(
            "Got it. I'll remember that."
        )

        return True

    # Memory
    if lower_command == "memory":

        if not memory:

            speak(
                "I don't have any permanent memories yet."
            )

            return True

        print()
        print("🧠 WHAT I REMEMBER:")
        print()

        for index, item in enumerate(memory, 1):

            print(f"{index}. {item}")

        print()

        memory_text = ". ".join(memory)

        speak(
            "Here's what I remember. "
            + memory_text
        )

        return True

    # Forget
    if lower_command == "forget":

        memory.clear()

        save_memory(memory)

        speak(
            "All permanent memories have been cleared."
        )

        return True

    return False


# ============================================================
# 👋 EXIT COMMANDS
# ============================================================

def is_exit_command(command):

    commands = [
        "exit",
        "quit",
        "bye",
        "goodbye",
        "shutdown",
        "shut down"
    ]

    return command.lower().strip() in commands


# ============================================================
# 🐉 START DRACARYS
# ============================================================

def main():

    print()
    print("====================================================")
    print("🐉 DRACARYS - MY PERSONAL AI ASSISTANT")
    print("====================================================")
    print()
    print("Model:", MODEL)
    print("Memory:", MEMORY_FILE)
    print()
    print("Commands:")
    print("  remember <something>  -> Save a permanent memory")
    print("  memory                -> Show saved memories")
    print("  forget                -> Delete saved memories")
    print("  exit                  -> Shut down DRACARYS")
    print()
    print("Press ENTER to speak.")
    print("Type something instead if you want to use keyboard input.")
    print()
    print("====================================================")
    print()

    speak(
        "Hello Dhanush. I am DRACARYS, "
        "your personal AI assistant. "
        "I am online and ready."
    )

    while True:

        try:

            print()
            user_input = input(
                "You (ENTER = voice, or type): "
            )

            # ==================================================
            # 🎤 VOICE MODE
            # ==================================================

            if user_input.strip() == "":

                user_message = listen()

                if not user_message:
                    continue

            # ==================================================
            # ⌨️ TEXT MODE
            # ==================================================

            else:

                user_message = user_input.strip()

            # ==================================================
            # EXIT
            # ==================================================

            if is_exit_command(user_message):

                speak(
                    "Goodbye Dhanush. "
                    "I'll be here when you return."
                )

                break

            # ==================================================
            # MEMORY COMMANDS
            # ==================================================

            if handle_memory_command(user_message):

                continue

            # ==================================================
            # AI
            # ==================================================

            print()
            print("🧠 DRACARYS IS THINKING...")

            answer = ask_dracarys(
                user_message
            )

            # ==================================================
            # DISPLAY + SPEAK
            # ==================================================

            print()
            print("🐉 DRACARYS:", answer)
            print()

            speak(answer)

        except KeyboardInterrupt:

            print()
            print()

            speak(
                "Shutting down safely."
            )

            break

        except Exception as error:

            print()
            print("DRACARYS ERROR:", error)
            print()

            speak(
                "Something went wrong."
            )


# ============================================================
# 🚀 RUN
# ============================================================

if __name__ == "__main__":

    main()
