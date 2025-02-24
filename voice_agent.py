import ollama
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import speech_recognition as sr

class AIVoiceAgent:
    def __init__(self):
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY", "sk_6986260cd672fa29b9860d55828da9942806d6b87d824453")
        )
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.voice_name = "Rachel"
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }

        self.full_transcript = [
            {"role": "system", "content": "You are a robot called TARS created by SecretLabz. Answer questions in less than 300 characters."},
        ]

    def listen_to_user(self):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            audio = self.recognizer.listen(source)
            
            try:
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                print("Sorry, I didn't understand that.")
                return None
            except sr.RequestError:
                print("Sorry, I'm having trouble accessing the speech recognition service.")
                return None

    def generate_ai_response(self, user_text):
        self.full_transcript.append({"role": "user", "content": user_text})
        print(f"\nUser: {user_text}")

        ollama_response = ollama.chat(
            model="mistral",
            messages=self.full_transcript
        )
    
        if "message" not in ollama_response or "content" not in ollama_response["message"]:
            print("Error: Ollama didn't return a valid response.")
            return

        ai_text = ollama_response["message"]["content"].strip()
        print("TARS:", ai_text)

        try:
            audio = self.client.generate(
                text=ai_text,
                voice=self.voice_name,
                model="eleven_monolingual_v1",
                voice_settings=self.voice_settings
            )
            play(audio)
        except Exception as e:
            print(f"Error generating speech: {e}")

        self.full_transcript.append({"role": "assistant", "content": ai_text})

    def start_chat(self):
        print("Hello! I'm TARS. How can I assist you today?")
        while True:
            user_input = self.listen_to_user()
            
            if user_input is None:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("TARS: Goodbye!")
                try:
                    audio = self.client.generate(
                        text="Goodbye!",
                        voice=self.voice_name,
                        model="eleven_monolingual_v1"
                    )
                    play(audio)
                except Exception as e:
                    print(f"Error generating speech: {e}")
                break
            
            self.generate_ai_response(user_input)

if __name__ == "__main__":
    ai_voice_agent = AIVoiceAgent()
    ai_voice_agent.start_chat()