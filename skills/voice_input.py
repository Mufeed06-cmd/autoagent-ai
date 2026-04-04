import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_once() -> str:
    """
    Listen from microphone and return recognized text.
    Returns empty string if nothing heard or error.
    """
    with sr.Microphone() as source:
        print("[Voice] Calibrating mic...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[Voice] Listening... speak now")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("[Voice] No speech detected.")
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"[Voice] Heard: {text}")
        return text
    except sr.UnknownValueError:
        print("[Voice] Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"[Voice] Google API error: {e}")
        return ""