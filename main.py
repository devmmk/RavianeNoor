from flask import Flask, request, jsonify, send_file, render_template
from openai import OpenAI
import io, json, os, time, requests
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from bs4 import BeautifulSoup
import speech_recognition as sr
from requests import post, get
import pyttsx3

class Translate:
    def __init__(self):
        self.url = 'https://api.reverso.net/translate/v1/translation'
        self.headers = {
            'content-type':'application/json',
            'user-agent': 'Cy'
        }
    
    # lang input: eng, per
    def text_to_text(self, src_lang, dst_lang, text):
        data = {
            "format": "text",
            "from": src_lang,
            "to": dst_lang,
            "input": text,
            "options": {"origin": "translation.web"}
        }
        try:
            request = post(url=self.url, headers=self.headers, data=json.dumps(data))
            result = request.json()
            return result['translation'][0]
        except BaseException as e:
            print(e)
    
    
    # lang input: fa-IR, en-US
    def transcribe_audio(self, audio_path, lang="fa-IR"):
        with sr.AudioFile(audio_path) as source:
            r = sr.Recognizer()
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data, language=lang)
            return text
        
    
    def sound_to_text(self, src_lang, dst_lang, sound_path):
        try:
            result = self.transcribe_audio(sound_path, src_lang)
        except BaseException as e:
            print(e)
        else:
            translated = self.text_to_text(src_lang, dst_lang, result)
            return translated
            
    
    def image_to_text(self, src_lang, dst_lang, image_path):
        try:
            image = Image.open(image_path)
            image = image.convert('L')
            image = image.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            text = pytesseract.image_to_string(image,  lang=src_lang)
        except BaseException as e:
            print(e)
        else:
            #TODO change the src lang to something else
            translated = self.text_to_text(src_lang, dst_lang, text)
            return translated
    
    def text_to_speech(self, text, dst_lang):
        engine = pyttsx3.init(driverName='espeak')
        engine.setProperty('voice', 'fa')  # Set Persian language
        engine.setProperty('rate', 150)  # Adjust speed
        engine.say(text)
        engine.save_to_file(text, "output.mp3")
        engine.runAndWait()
        return "output.mp3"

class WikiShahid:
    def __init__(self):
        pass
    
    def search(self, query):

        url = 'https://wikishahid.com/ajax/search/1732253172372'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded;',
            'Origin': 'https://wikishahid.com',
            'Connection': 'keep-alive',
            'Referer': 'https://wikishahid.com/',
            'Cookie': 'ci_session=Uk9sA83V6cR73DVoM92Mr85hgwR7n1QyOWY%2BaFqzDiODSZSYV%2BCOb04T9bu8ZkyQkMZKqogQg6%2Be5UE%2FUp45FFtuxWW7E15O%2BKSY6BCIb9NPBE4UveHvHXyi7vO9yG7OeR5PdSizc7nquLbTRCCSvCLJX%2F2e7WbMtJ7HTrtAFC%2BNYPjx6q4s7n%2FcSRBRlzax9ekMJM3phIgGYdzytFriozVkBUQXgfIj82S5Kssz81vAOy0TeT4dQCMsKODu%2FQEX618064VzsHqLIV0RwjrG4KIUoWVTSX1RKWhmqvXHO5aoSdLWjYYPKYZB1uJ2OurCGJp0sNtSYgAnOs0HQP3sMQj47jX3ftmbfYzGHOw%2F9qoWF5jdBC762DiwkQa1W4IA',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0'
        }
        data = {
            'key': query  # Unicode for the string
        }
        try:
            response = requests.post(url, headers=headers, data=data)
        except BaseException as e:
            print(e)
        else:
            result = {}
            soup = BeautifulSoup(response.text)
            for i in soup.find_all('div'):
                result.update({i.text: ""})
        
        return result
    
    def get_details(self, name):
        url = f"https://wikishahid.com/{name}"
        try:
            response = requests.get(url)
            print(response.text)
        except BaseException as e:
            print(e)
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('tbody')
            text = table.get_text(separator=' ', strip=True)
            return text.replace('ذخیره مقاله با فرمت پی دی اف', '')
            

            
"""
class AIChatBot:
    def __init__(self):         
        self.base_url = "https://api.aimlapi.com/v1"
        self.api_key = "c9182ee11f9e4d97910c994c17e6781c"
        self.api = OpenAI(api_key=self.api_key, base_url=self.base_url)


    def talk_to_ai(self, text):
        messages=[
                {"role": "system", "content": "You are a language learning assistant and partner to improving language skills."},
                {"role": "user", "content": text},
        ]

        completion = self.api.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=256,
        )

        response = completion.choices[0].message.content
        return response
"""

class AIChatBot:
    def __init__(self):
        self.url = "https://api3.haji-api.ir/majid/gpt/4?q={}&license=HPegOmZxczNMUNLG38IZWSH4WHFuaWCBVYdt8Iu1AfIGjBVMo71fZA0idUd"
        self.role = "تو یک راهنما در زمینه شهدای دفاع مقدس ایران و شهدای اسلام هستی. لطفا به سوالات و پیام های دیگر در زمینه های دیگر و خارج از احکام اسلام پاسخ نده. متن کاربر:\n\n"
    
    def talk_to_ai(self, text):
        response = get(self.url.format(self.role + text))
        print(response.text)
        return response.json()['result']
        

app = Flask(__name__)
translate = Translate()
ai = AIChatBot()

@app.route("/")
def handler():
    return "سلام"

@app.route("/text", methods=['POST'])
def text_handler():
    data = request.get_json()
    src_lang = data.get('src_lang')
    dst_lang = data.get('dst_lang')
    text = data.get('text')
    result = translate.text_to_text(src_lang, dst_lang, text)
    return jsonify({"translation": result})

@app.route("/audio", methods=['POST'])
def audio_handler():
    data = request.files['audio']
    src_lang = request.form.get('src_lang')
    dst_lang = request.form.get('dst_lang')
    
    temp_path = "temp_audio.wav"
    data.save(temp_path)
    
    translate = Translate()
    result = translate.sound_to_text(src_lang, dst_lang, temp_path)
    
    os.remove(temp_path)
    return jsonify({"translation": result})

@app.route("/image", methods=['POST'])
def image_handler():
    data = request.files['image']
    src_lang = request.form.get('src_lang')
    dst_lang = request.form.get('dst_lang')
    
    temp_path = "temp_image.png"
    data.save(temp_path)
    
    translate = Translate()
    result = translate.image_to_text(src_lang, dst_lang, temp_path)
    
    os.remove(temp_path)
    return jsonify({"translation": result})

@app.route("/ai-chat", methods=['GET'])
def ai_chat_handler():
    return render_template('./index.html')

@app.route("/ai", methods=['POST'])
def ai_chatbot():
    print(request)
    print(request.form)
    data = request.form.get('message')
    return ai.talk_to_ai(data)

@app.route("/tts", methods=['POST'])
def speech_handler():
    data = request.form.get('message')
    dst_lang = request.form.get('dst_lang')
    result = translate.text_to_speech(data, dst_lang)
    return send_file(result, as_attachment=True)

@app.route("/search", methods=['POST'])
def wiki_handler():
    data = request.form.get('query')
    wiki = WikiShahid()
    return wiki.search(data)

@app.route("/details", methods=['POST'])
def wiki_details():
    data = request.form.get('name')
    wiki = WikiShahid()
    return wiki.get_details(data)

if __name__ == "__main__":
    app.run(debug=True)
