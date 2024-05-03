from typing import Optional
import speech_recognition as sr
import os, g4f, time, requests
from termcolor import colored
import threading, base64
import cloudinary
from cloudinary.uploader import upload

""" CONSTANTS """

AUDIO_DIR = "./mp3"
LIMIT_TEXT = 298
ENDPOINTS = [
    "https://tiktok-tts.weilnet.workers.dev/api/generation",
    "https://tiktoktts.com/api/tiktok-tts",
]
CURRENT_ENDPOINT = 0

""" CONFIGURATIONS """
cloudinary.config(
    cloud_name="dqrw1zi7d",
    api_key="147524246886253",
    api_secret="EoZUZSbCDj0gx7psb9YFU3aYpZc",
)


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

    def stop(self):
        self.listening = False

    @staticmethod
    def find_model(model_name):
        model_name = model_name.lower()
        if model_name == "gpt_4":
            return g4f.models.gpt_4
        if model_name == "mistral":
            return g4f.models.mistral_7b
        if model_name == "llama_13b":
            return g4f.models.llama2_13b
        if model_name == "llama_70b":
            return g4f.models.llama2_70b
        if model_name == "claude_2":
            return g4f.models.claude_v2
        return g4f.models.gpt_35_turbo_16k_0613

    @staticmethod
    def create_audio_dir(dir: Optional[str] = AUDIO_DIR) -> None:
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except OSError as e:
                print(colored(f"Failed to create {dir}: {str(e)}"))

    def listen(self):
        while self.listening:
            with sr.Microphone() as source:
                print(colored("[+] Listening ..", "blue"))
                audio_text = self.recognizer.listen(source)
                try:
                    text = self.recognizer.recognize_google(
                        audio_text, language=self.language
                    )
                    print(colored(f'[+]"{text}"', "green"))
                    if text.lower() == self.stop_trigger or text.lower().startswith(
                        self.stop_trigger
                    ):
                        print(colored("[*] Stopping in a few ...."))
                        self.stop()
                    else:
                        self.current_lesson.append(text)
                except Exception as err:
                    print(colored("[x] Sorry I didn't get that", "red"))

    def summarize(self):
        print(colored("[=>] Summarizing the text ...", "magenta"))
        full_text = ",".join(self.current_lesson)
        prompt = format_prompt(full_text)
        self.model = self.find_model(self.model)
        response = g4f.ChatCompletion.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        if response is not None:
            self.create_audio_dir()
            audio_path = f"{AUDIO_DIR}/{int(time.time())}.mp3"

            """ continue at this point """

        else:
            print(colored(f"[!] {self.model} did not return any response", "red"))

    def convert_text_to_speech(
        self, text: str, file_name: Optional[str] = "./tiller.mp3"
    ) -> None:
        res = [
            text[y - LIMIT_TEXT : y]
            for y in range(LIMIT_TEXT, len(text) + LIMIT_TEXT, LIMIT_TEXT)
        ]
        all_bytes = [None] * len(res)

        def generate_audio(index: int, text: str, voice: str) -> bytes:
            url = f"{ENDPOINTS[CURRENT_ENDPOINT]}"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            data = {"text": text, "voice": voice}
            r = requests.post(url=url, headers=headers, json=data)
            if r.headers.get("Content-Type") == "application/json; charset=UTF-8":
                audio_bytes = r.json()["data"]
            else:
                audio_bytes = str(r.content).split('"')[5]
            all_bytes[index] = audio_bytes

        threads = []
        for index in range(len(res)):
            thread = threading.Thread(
                target=generate_audio, args=(index, res[index], self.voice)
            )
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
            
        base64_data = "".join(all_bytes)
        audio_bytes = base64.b64decode(base64_data)
        with open(file_name, "wb") as file:
            file.write(audio_bytes)
            print(colored(f"[+] audio bytes saved to: {file_name}", "green"))

    @staticmethod
    def cloudinary_upload(path: str) -> str:
        public_id = f"Tiller_{int(time.time())}"
        results = upload(path, public_id=public_id, resource_type="raw")
        return results["url"]
