import pyaudio
import wave
import openai
import os
import requests

# Set up OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def record_audio(filename, duration=10):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording... Speak your image prompt.")
    frames = []

    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")
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
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

if __name__ == "__main__":
    audio_file = "temp_audio.wav"
    record_audio(audio_file, duration=10)
    prompt = transcribe_audio(audio_file)
    print(f"Transcribed prompt: {prompt}")
    if prompt.strip():
        image_url = generate_image(prompt)
        print(f"Image generated: {image_url}")
        # Download and save the image
        response = requests.get(image_url)
        with open("generated_image.png", "wb") as f:
            f.write(response.content)
        print("Image saved as generated_image.png")
    else:
        print("No speech detected.")
    # Clean up
    if os.path.exists(audio_file):
        os.remove(audio_file)