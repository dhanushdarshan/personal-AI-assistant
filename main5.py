import time
import numpy as np
import pyaudiowpatch as pyaudio
from openwakeword.model import Model


# ============================================================
# DRACARYS WAKE-WORD TEST
# ============================================================

print()
print("=" * 55)
print("🐉 DRACARYS WAKE-WORD ENGINE TEST")
print("=" * 55)
print()
print("🎤 Listening continuously...")
print("Say:  Hey Jarvis")
print("Press CTRL+C to stop.")
print()


# ------------------------------------------------------------
# Load wake-word model
# ------------------------------------------------------------

model = Model(
    wakeword_models=["hey_jarvis"]
)

print("✅ Wake-word model loaded.")
print()


# ------------------------------------------------------------
# Microphone setup
# ------------------------------------------------------------

audio = pyaudio.PyAudio()

try:
    device = audio.get_default_input_device_info()
    device_index = int(device["index"])

    print(f"🎤 Microphone: {device['name']}")
    print()

except Exception as e:
    print(f"❌ Could not find microphone: {e}")
    audio.terminate()
    raise SystemExit


# ------------------------------------------------------------
# Open microphone
# ------------------------------------------------------------

RATE = 16000
CHANNELS = 1
CHUNK = 1280

stream = audio.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=device_index,
    frames_per_buffer=CHUNK
)


# ------------------------------------------------------------
# Listen continuously
# ------------------------------------------------------------

try:

    while True:

        data = stream.read(
            CHUNK,
            exception_on_overflow=False
        )

        audio_data = np.frombuffer(
            data,
            dtype=np.int16
        )

        prediction = model.predict(audio_data)

        for wakeword, score in prediction.items():

            if score > 0.5:

                print()
                print("=" * 55)
                print("🐉 WAKE WORD DETECTED!")
                print(f"🔥 {wakeword}")
                print(f"📊 Confidence: {score:.2f}")
                print("=" * 55)
                print()

                # Small cooldown so it doesn't trigger repeatedly
                time.sleep(2)

except KeyboardInterrupt:

    print()
    print("🛑 Wake-word test stopped.")

finally:

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("🐉 DRACARYS wake engine closed.")
