import speech_recognition as sr
from termcolor import colored
AUDIO_DIR = "./mp3"


def format_prompt(prompt: str) -> str:
    return f"""
        Please summarize the following paragraph. Ensure the summary is concise yet captures all essential information:

        PARAGRAPH: {prompt}

        Avoid unnecessary details and focus on the key points. Provide a clear explanation where needed. Do not include any irrelevant information or markdown.

        Avoid including phrases such as "Here is a possible summary" or any other non-essential elements. Also, refrain from mentioning the prompt itself or any extraneous terms. Focus solely on providing a succinct yet comprehensive summary of the provided text.
        """


class Transcribe:
    def __init__(self, model: str = "", lang: str = "eng", voice: str = "") -> None:
        self.model = model
        self.language = lang
        self.voice = voice
        self.listening: bool = False
        self.current_lesson = []
        self.model = model 
        self.recognizer = sr.Recognizer()
        self.stop_trigger = "stopp"
    
    @property
    def listening(self):
        return self.listening
    
    @property.setter
    def listening(self, value: bool):
        self.listening = value
        
    def listen(self):
        while(self.listening):
            with sr.Microphone() as source:
                print(colored("[+] Listening ..", "blue"))
                audio_text = self.recognizer.listen(source)
                try:
                    text = self.recognizer.recognize_google(audio_text, language=self.language)
                    print(colored(f"[+]\"{text}\"", "green"))
                    if text.lower() == self.stop_trigger or text.lower().startswith(self.stop_trigger):
                        print(colored("[*] Stopping in a few ...."))
                        self.stop()
                    else:
                        self.current_lesson.append(text)
                except:
                    print(colored("[-] Sorry I didn't get that", "red"))
        
    def stop(self):
        self.listening = False
    
