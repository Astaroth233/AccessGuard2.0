import pyaudio
import wave
import speech_recognition as sr

KEYWORD = "Hello"  # Define the keyword

def capture_voice_data():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    rate = 44100
    record_seconds = 5  # Adjust the recording duration as needed

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print(f"Recording... Please say the keyword: '{KEYWORD}'")

    frames = []
    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    filename = 'data/temp.wav'
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        spoken_text = recognizer.recognize_google(audio)
        print(f"You said: {spoken_text}")
        if KEYWORD.lower() in spoken_text.lower():
            with open(filename, 'rb') as f:
                voice_data = f.read()
            return voice_data
        else:
            print("Keyword mismatch. Voice data not captured.")
            return None
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
