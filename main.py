import threading
import streamlit as st
import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import json
import time

# API Keys
newsapi = "221d457b9082416188edd84090b0c7fd"
GEMINI_API_KEY = "AIzaSyCO6nhph90SnOLuOMrYkAQJ24bFm_UV5nA"

# Text-to-Speech setup
engine = pyttsx3.init()
def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    t = threading.Thread(target=run)
    t.start()
    
# Gemini AI Call
def googleGeminiAI(query):
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    if "summarize" not in query.lower():
        query += " summarize in short."

    data = {"contents": [{"parts": [{"text": query}]}]}
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            output = response.json()
            ai_response = output.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            return ai_response
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"API Error: {str(e)}"

# Command Processing
def processCommand(command):
    command = command.lower()
    if command == "open google":
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif command == "open youtube":
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif command == "open linkedin":
        webbrowser.open("https://www.linkedin.com")
        return "Opening LinkedIn."
    elif "news" in command:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            return "\n".join([article['title'] for article in articles[:5]])
        else:
            return "Failed to fetch news."
    elif "ai" in command or "what is" in command or "who is" in command or "explain" in command:
        return googleGeminiAI(command)
    else:
        return "Command not recognized."

# Streamlit UI
st.title("Voice Assistant: Jarvis")
st.markdown("Talk to Jarvis using voice or text. Must say 'Jarvis' after Start Listening.")

# Session state initialization
if "listening" not in st.session_state:
    st.session_state.listening = False

if st.button("Start Listening"):
    st.session_state.listening = True
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say 'Jarvis' to activate...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            keyword = recognizer.recognize_google(audio)
            if keyword.lower() == "jarvis":
                speak("Yes")
                st.success("Jarvis activated! Now speak your command...")
                audio = recognizer.listen(source, timeout=5)
                try:
                    command = recognizer.recognize_google(audio)
                    st.write(f"You said: {command}")
                    response = processCommand(command)
                    st.success(response)
                    speak(response)
                except sr.UnknownValueError:
                    st.warning("Couldn't understand. Speak again.")
                    speak("Speak again")
        except sr.WaitTimeoutError:
            st.warning("No keyword detected. Try again.")

if st.button("Stop Listening"):
    st.session_state.listening = False
    st.success("Stopped. Click 'Start Listening' to begin again.")

text_input = st.text_input("Or type your command:")
if st.button("Submit Text Command"):
    if text_input:
        result = processCommand(text_input)
        st.success(result)
        speak(result)
    else:
        st.warning("Please enter a command.")
