import os
import requests
import json
import tempfile
import wave
import pyaudio
import playsound

# Assuming you have the OpenAI API key set as an environment variable
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    print("Please set the OPENAI_API_KEY environment variable.")
    exit(1)

def record_audio(filename, duration=5):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    print("Recording...")
    frames = []
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(filename):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    files = {
        "file": open(filename, "rb"),
        "model": (None, "whisper-1"),
    }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise Exception(f"Transcription failed: {response.text}")
    return response.json()["text"]

def translate_text(text, source_lang, target_lang):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    prompt = f"Translate the following text from {source_lang} to {target_lang}: {text}"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Translation failed: {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()

def text_to_speech(text, filename):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy",  # Can change to other voices like echo, fable, onyx, nova, shimmer
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"TTS failed: {response.text}")
    with open(filename, "wb") as f:
        f.write(response.content)

def main():
    source_lang = input("Enter source language (e.g., English): ")
    target_lang = input("Enter target language (e.g., French): ")
    duration = int(input("Enter recording duration in seconds: "))

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        audio_file = temp_audio.name

    record_audio(audio_file, duration)
    transcribed_text = transcribe_audio(audio_file)
    print(f"Transcribed: {transcribed_text}")

    translated_text = translate_text(transcribed_text, source_lang, target_lang)
    print(f"Translated: {translated_text}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_speech:
        speech_file = temp_speech.name

    text_to_speech(translated_text, speech_file)
    playsound.playsound(speech_file)

    # Clean up temp files
    os.unlink(audio_file)
    os.unlink(speech_file)

if __name__ == "__main__":
    main()