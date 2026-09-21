import os
import sys
import json
import wave
import io
import requests
import subprocess

# ============================================================
# AUDIO
# ============================================================

try:
    import pyaudiowpatch as pyaudio
    import speech_recognition as sr

    AUDIO_AVAILABLE = True

except Exception as e:
    AUDIO_AVAILABLE = False
    AUDIO_ERROR = str(e)


# ============================================================
# WEB SEARCH
# ============================================================

try:
    from ddgs import DDGS
    WEB_SEARCH_AVAILABLE = True
except Exception:
    WEB_SEARCH_AVAILABLE = False


# ============================================================
# CONFIG
# ============================================================

ASSISTANT_NAME = "DRACARYS"
USER_NAME = "Dhanush"

MODEL = "llama3.2:3b"

OLLAMA_URL = "http://localhost:11434/api/chat"

MEMORY_FILE = "memory.json"


# ============================================================
# MEMORY
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

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def save_memory():

    try:

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

    except Exception as e:

        print(f"❌ Memory save error: {e}")


memory = load_memory()


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(text):

    if not text:
        return

    try:

        safe_text = str(text).replace(
            "'",
            "''"
        )

        powershell_script = f"""
Add-Type -AssemblyName System.Speech

$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer

$voice.Volume = 100
$voice.Rate = 0

$voice.Speak('{safe_text}')

$voice.Dispose()
"""

        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:

        print(f"🔊 Speech error: {e}")


# ============================================================
# MICROPHONE - DIRECT PYAUDIOWPATCH
# ============================================================

def record_audio():

    """
    Records microphone directly using PyAudioWPatch.

    This avoids SpeechRecognition's sr.Microphone()
    dependency problem.
    """

    if not AUDIO_AVAILABLE:

        print("\n❌ Audio system unavailable.")

        if "AUDIO_ERROR" in globals():
            print(AUDIO_ERROR)

        return None

    audio = None
    stream = None

    try:

        print()
        print("🎤 DRACARYS IS LISTENING...")
        print("👉 Speak now!")
        print("🎙️ Recording for up to 8 seconds...")

        audio = pyaudio.PyAudio()

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        RECORD_SECONDS = 8

        # ----------------------------------------------------
        # Find a suitable input device
        # ----------------------------------------------------

        device_index = None

        try:

            default_device = (
                audio.get_default_input_device_info()
            )

            device_index = int(
                default_device["index"]
            )

            print(
                f"🎤 Microphone: "
                f"{default_device['name']}"
            )

        except Exception:

            print(
                "⚠️ Could not automatically find "
                "default microphone."
            )

        # ----------------------------------------------------
        # Open microphone
        # ----------------------------------------------------

        if device_index is not None:

            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )

        else:

            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

        frames = []

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        for _ in range(
            int(
                RATE / CHUNK *
                RECORD_SECONDS
            )
        ):

            data = stream.read(
                CHUNK,
                exception_on_overflow=False
            )

            frames.append(data)

        print("🛑 Recording finished.")

        # ----------------------------------------------------
        # Close stream
        # ----------------------------------------------------

        stream.stop_stream()
        stream.close()
        stream = None

        sample_width = audio.get_sample_size(
            FORMAT
        )

        audio.terminate()
        audio = None

        # ----------------------------------------------------
        # Create WAV in memory
        # ----------------------------------------------------

        wav_buffer = io.BytesIO()

        with wave.open(
            wav_buffer,
            "wb"
        ) as wav_file:

            wav_file.setnchannels(
                CHANNELS
            )

            wav_file.setsampwidth(
                sample_width
            )

            wav_file.setframerate(
                RATE
            )

            wav_file.writeframes(
                b"".join(frames)
            )

        wav_buffer.seek(0)

        return wav_buffer

    except Exception as e:

        print(
            f"❌ Microphone recording error: {e}"
        )

        if stream is not None:

            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass

        if audio is not None:

            try:
                audio.terminate()
            except Exception:
                pass

        return None


# ============================================================
# SPEECH TO TEXT
# ============================================================

def listen():

    if not AUDIO_AVAILABLE:

        print(
            "❌ Audio packages are unavailable."
        )

        return ""

    wav_audio = record_audio()

    if wav_audio is None:

        return ""

    try:

        recognizer = sr.Recognizer()

        print(
            "🧠 Processing your voice..."
        )

        with sr.AudioFile(
            wav_audio
        ) as source:

            audio_data = recognizer.record(
                source
            )

        text = recognizer.recognize_google(
            audio_data,
            language="en-IN"
        )

        print()
        print(
            f"YOU SAID: {text}"
        )

        return text.strip()

    except sr.UnknownValueError:

        print(
            "❌ I couldn't understand what you said."
        )

        return ""

    except sr.RequestError as e:

        print(
            f"❌ Speech recognition error: {e}"
        )

        return ""

    except Exception as e:

        print(
            f"❌ Speech-to-text error: {e}"
        )

        return ""


# ============================================================
# WEB SEARCH
# ============================================================

def web_search(query):

    if not WEB_SEARCH_AVAILABLE:

        print(
            "❌ Web search is unavailable."
        )

        return []

    print()
    print(
        "🌐 DRACARYS IS SEARCHING THE WEB..."
    )

    print(
        f"🔎 {query}"
    )

    results = []

    try:

        with DDGS() as search:

            found = search.text(
                query,
                max_results=6
            )

            for item in found:

                title = item.get(
                    "title",
                    ""
                )

                body = item.get(
                    "body",
                    ""
                )

                url = item.get(
                    "href",
                    ""
                )

                if title or body:

                    results.append(
                        {
                            "title": title,
                            "body": body,
                            "url": url
                        }
                    )

        print(
            f"✅ Found {len(results)} web results."
        )

    except Exception as e:

        print(
            f"❌ Web search error: {e}"
        )

    return results


# ============================================================
# WHEN TO SEARCH WEB
# ============================================================

def needs_web_search(query):

    q = query.lower().strip()

    # Explicit search.
    if q.startswith("search "):
        return True

    current_words = [

        "today",
        "latest",
        "current",
        "currently",
        "recent",
        "recently",
        "news",

        "this week",
        "this month",
        "this year",

        "2026",

        "price",
        "cost",

        "weather",

        "score",
        "scores",

        "result",
        "results",

        "update",
        "updates",

        "release",
        "released",

        "launch",
        "launched",

        "stock",
        "stocks",

        "market"
    ]

    for word in current_words:

        if word in q:
            return True

    factual_starts = [

        "who is ",
        "who was ",

        "what is ",
        "what was ",

        "where is ",
        "where was ",

        "when was ",
        "when did ",
        "when does ",
        "when will ",

        "how much is ",
        "how much does ",

        "which is ",
        "which are "
    ]

    for phrase in factual_starts:

        if q.startswith(phrase):
            return True

    return False


# ============================================================
# FORMAT WEB RESULTS
# ============================================================

def format_web_results(results):

    if not results:
        return ""

    text = ""

    for number, result in enumerate(
        results,
        start=1
    ):

        text += f"""

SOURCE {number}

TITLE:
{result.get("title", "")}

INFORMATION:
{result.get("body", "")}

URL:
{result.get("url", "")}

"""

    return text


# ============================================================
# SHOW SOURCES
# ============================================================

def display_sources(results):

    if not results:
        return

    print()
    print(
        "=================================================="
    )

    print(
        "🌐 WEB SOURCES"
    )

    print(
        "=================================================="
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        print()
        print(
            f"[{number}] "
            f"{result.get('title', 'Unknown')}"
        )

        print(
            result.get(
                "url",
                ""
            )
        )

    print()
    print(
        "=================================================="
    )


# ============================================================
# DRACARYS SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are DRACARYS.

You are Dhanush's personal AI assistant.

Your name is DRACARYS.

You run locally using Ollama.

IMPORTANT:

- Never call yourself ChatGPT.
- Never introduce yourself as Llama.
- Your name is DRACARYS.
- Be helpful and natural.
- Keep spoken answers reasonably concise.
- Never knowingly invent facts.
- Web search information is the primary source
  for factual/current questions.
- Never pretend you searched the internet
  if no web results were provided.
- If supplied sources are insufficient,
  say that you are uncertain.
- If sources disagree, mention it.
- Use saved memory only when relevant.
- Do not expose private memories unnecessarily.

"""


# ============================================================
# CONVERSATION
# ============================================================

conversation = []


# ============================================================
# ASK OLLAMA
# ============================================================

def ask_dracarys(
    user_message,
    web_results=None
):

    global conversation

    messages = []

    # --------------------------------------------------------
    # System
    # --------------------------------------------------------

    messages.append(
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    )

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    if memory:

        memory_text = "\n".join(
            f"- {item}"
            for item in memory
        )

        messages.append(
            {
                "role": "system",
                "content":
                    "Relevant saved memories:\n"
                    + memory_text
            }
        )

    # --------------------------------------------------------
    # Web
    # --------------------------------------------------------

    if web_results:

        web_context = format_web_results(
            web_results
        )

        messages.append(
            {
                "role": "system",
                "content":
                    """
WEB SEARCH RESULTS:

"""
                    + web_context
                    +
                    """

Use the supplied web information
as factual reference.

Do not invent unsupported details.

If the information is insufficient,
say so.

"""
            }
        )

    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    messages.extend(
        conversation[-10:]
    )

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

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

                "stream": False,

                "options": {
                    "temperature": 0.15
                }
            },

            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data[
            "message"
        ][
            "content"
        ].strip()

        # Save conversation.
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
            "I cannot connect to Ollama. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "The AI response took too long. "
            "Please try again."
        )

    except Exception as e:

        print(
            f"❌ Ollama error: {e}"
        )

        return (
            "Something went wrong with "
            "my local AI brain."
        )


# ============================================================
# MEMORY COMMANDS
# ============================================================

def handle_memory(command):

    global memory

    lower = command.lower().strip()

    # --------------------------------------------------------
    # REMEMBER
    # --------------------------------------------------------

    if lower.startswith("remember "):

        item = command[9:].strip()

        if not item:

            return (
                "Tell me what you want me to remember."
            )

        if item in memory:

            return (
                "I already remember that."
            )

        memory.append(item)

        save_memory()

        return (
            "I'll remember that, Dhanush."
        )

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if lower == "memory":

        if not memory:

            return (
                "My memory is empty."
            )

        print()
        print(
            "=================================================="
        )

        print(
            "💾 DRACARYS MEMORY"
        )

        print(
            "=================================================="
        )

        for number, item in enumerate(
            memory,
            start=1
        ):

            print(
                f"{number}. {item}"
            )

        print(
            "=================================================="
        )

        return (
            f"I have {len(memory)} saved memories."
        )

    # --------------------------------------------------------
    # FORGET
    # --------------------------------------------------------

    if lower == "forget":

        memory.clear()

        save_memory()

        return (
            "All saved memories have been cleared."
        )

    return None


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(message):

    message = message.strip()

    if not message:
        return False

    lower = message.lower()

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if lower in [
        "exit",
        "quit",
        "bye",
        "shutdown"
    ]:

        print()
        print(
            "🐉 DRACARYS: Shutting down."
        )

        speak(
            "Shutting down. "
            "See you later, Dhanush."
        )

        return True

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    memory_response = handle_memory(
        message
    )

    if memory_response is not None:

        print()
        print(
            f"🐉 DRACARYS: "
            f"{memory_response}"
        )

        speak(
            memory_response
        )

        return False

    # --------------------------------------------------------
    # WEB
    # --------------------------------------------------------

    results = []

    if needs_web_search(message):

        search_query = message

        if lower.startswith("search "):

            search_query = message[7:].strip()

        results = web_search(
            search_query
        )

        display_sources(
            results
        )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    answer = ask_dracarys(
        message,
        results
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print()
    print(
        "🐉 DRACARYS:"
    )

    print(
        answer
    )

    print()

    # --------------------------------------------------------
    # SPEAK
    # --------------------------------------------------------

    speak(answer)

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print(
        "=================================================="
    )

    print(
        "             🐉 DRACARYS ONLINE"
    )

    print(
        "=================================================="
    )

    print()

    print(
        f"🧠 AI Model       : {MODEL}"
    )

    print(
        "🌐 Web Search     : "
        + (
            "ENABLED"
            if WEB_SEARCH_AVAILABLE
            else "DISABLED"
        )
    )

    print(
        "💾 Memory         : ENABLED"
    )

    print(
        "🔊 Text-to-Speech : ENABLED"
    )

    print(
        "🎤 Microphone     : "
        + (
            "ENABLED"
            if AUDIO_AVAILABLE
            else "DISABLED"
        )
    )

    print()

    print(
        "Commands:"
    )

    print(
        "  remember <text>  → Save memory"
    )

    print(
        "  memory           → Show memory"
    )

    print(
        "  forget           → Clear memory"
    )

    print(
        "  search <query>   → Search web"
    )

    print(
        "  exit             → Shutdown"
    )

    print()

    print(
        "Press ENTER for voice."
    )

    print(
        "Or type a message."
    )

    print()

    print(
        "=================================================="
    )

    speak(
        "Dracarys is online."
    )

    while True:

        try:

            print()

            user_input = input(
                "⌨️ Type message or press ENTER for voice: "
            ).strip()

            # ------------------------------------------------
            # Voice mode
            # ------------------------------------------------

            if user_input == "":

                user_input = listen()

                if not user_input:

                    continue

            # ------------------------------------------------
            # Process
            # ------------------------------------------------

            should_exit = process_message(
                user_input
            )

            if should_exit:

                break

        except KeyboardInterrupt:

            print()

            print(
                "🐉 DRACARYS: Shutdown requested."
            )

            break

        except EOFError:

            print()

            print(
                "🐉 DRACARYS: Shutdown requested."
            )

            break

        except Exception as e:

            print()

            print(
                f"❌ Unexpected error: {e}"
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
