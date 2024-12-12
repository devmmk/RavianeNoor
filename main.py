from flask import Flask, request, jsonify, send_file, render_template
import io, json, os, time, requests, re
import pytesseract
from base64 import b64encode, b64decode
from PIL import Image, ImageEnhance, ImageFilter
from bs4 import BeautifulSoup
import speech_recognition as sr
from requests import post, get
import time

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
        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded;',
            'Origin': 'https://wikishahid.com',
            'Connection': 'keep-alive',
            'Referer': 'https://wikishahid.com/',
            'Cookie': 'ci_session=lMANhdjb99Bg1gqLfd4aVX3Bg0XOlm%2F7ACK9HRzeDXj6sX0NtIyPQAwimIpGm1DkYbjUptR6No8zZRcW2F0stNSJ99BMgzElXjZeRlqgzegTsX5URPTYivHan4cne9t6iHEcD70GdjWmOXtOylzrKf6rvVfTGqsGsdUlgXPdSWgEjuzzyO4zt%2Fmmj7Xa075Z5AAhfo51ZIKEnxl7TLf31jwscbYkukqMm%2Bf2sZzOJxxznABC8kC8asR%2B2DI23%2BztbR9eSdFR9uJjnmNJiBw9NL%2F%2B%2FCWcbkhHEDE%2F4Ly7kpSVktHHyXk2guSrv1zFyweuBpHqKBYL7YGfhqjPvM9gCh7ILAYRXdGiE5qRTs1DVeDM58zuOImrfXy8mxUk5wFn',
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
            result = []
            soup = BeautifulSoup(response.text)
            for i in soup.find_all('div'):
                result.append(i.text)        
            return result
    
    def get_details(self, name):
        url = f"https://wikishahid.com/{name}"
        print(name)
        try:
            response = requests.get(url)
            print(response.text)
        except BaseException as e:
            print(e)
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('tbody')
            text = table.get_text(separator=' ', strip=True).replace('ذخیره مقاله با فرمت پی دی اف', '').replace('[ ویرایش ]', '\n\n').replace('. ', '.\n').replace(name + ' ' + name, name)
            splited = text.splitlines()
            for line in splited:
                if 'فهرست مندرجات' in line:
                    splited.remove(line)
            return '\n'.join(splited)
    
    def search_grave(self, name):
        url = "https://www.golzar.info/?s=" + name
        req = get(url)
        text = req.text
        soup = BeautifulSoup(text, 'html.parser')
        divs_with_mart_sec = soup.find_all('div', class_='clomun-mart pad-10 pull-right')
        result = []
        for div in divs_with_mart_sec:
            for link in div.find_all('a'):
                if 'category' in link['href']:
                    continue
                else:
                    link = link['href']
                    break

            img = div.find('img')['src']
            result.append({'link': link, 'img': img, 'name': div.text})
        return result
    
    def get_grave(self, url):
        req = get(url)
        text = req.text
        soup = BeautifulSoup(text, 'html.parser')
        imgs = soup.find_all('img')
        wp_images = []
        for img in imgs:
            if 'wp-content/uploads' in img['src']:
                wp_images.append(img['src'])
        return wp_images[-1]
    
    def get_gps(self, url):
        req = get(url)
        text = req.text
        soup = BeautifulSoup(text, 'html.parser')
        lat_match = re.search(r'lat:\s*([-\d.]+)', text).group(0).replace('lat: ', '')
        lng_match = re.search(r'lng:\s*([-\d.]+)', text).group(0).replace('lng: ', '')
        return (lat_match, lng_match)

            

            
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
        self.role = """تو باید در نقش شهید حسین قجه ای به کاربر پاسخ بدی. متن زیر زندگینامه حسین قجه است:\n\n
    حسین علی قجه‌ای در ۱۴ شهریور ۱۳۳۷ در زرین شهر از شهرهای استان اصفهان به دنیا آمد.
عضو رسمی سپاه پاسداران انقلاب اسلامی بود و از فرماندهان لشکر ۲۷ محمد رسول‌الله محسوب می‌شد.
در جریان عملیات آزادسازی خرمشهر ، گردان سلمان فارسی به فرماندهی حسین قجه‌ای موفق به دفع سومین پاتک سنگین دو تیپ زرهی و مکانیزه سپاه سوم نیروی زمینی عراق در جاده اهواز / خرمشهر شد.
در جریان این مقاومت شش روزه، بیشتر نیروهای گردان و همچنین حسین قجه‌ای به شهادت رسیدند.
این واقعه در ۱۵ اردیبهشت ۱۳۶۱ رخ داد.
پیکر وی در گلستان شهدای زرین شهر به خاک سپرده شد.

به سوال هایی که خارج از این اطلاعات هستند و نمیدانی هم پاسخ نده. متن کاربر:\n\n
"""
    
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

@app.route("/search-grave", methods=['POST'])
def grave_search():
    data = request.form.get('name')
    wiki = WikiShahid()
    return wiki.search_grave(data)

@app.route("/grave", methods=['POST'])
def grave():
    data = request.form.get('url')
    wiki = WikiShahid()
    res = [wiki.get_grave(data), list(wiki.get_gps(data))]
    print(res)
    return res

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
