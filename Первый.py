import telebot
import requests
import openai
import os
from docx import Document
from googletrans import Translator
from telebot import types
import time
import logging
import json
from bs4 import BeautifulSoup

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен Telegram-бота
bot = telebot.TeleBot("")

# API ключ для OpenAI через openrouter.ai
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = ""

# API ключ для Google Search
google_api_key = ""

# Идентификатор Custom Search Engine
cse_id = ""

# API ключ для Prodia
prodia_api_key = ""

# Список моделей и стилей
models = [
    "absolutereality_v181.safetensors [3d9d4d2b]",
    "anything-v4.5-pruned.ckpt [65745d25]",
    "AOM3A3_orangemixs.safetensors [9600da17]",
    "deliberate_v2.safetensors [10ec4b29]",
    "dreamlike-photoreal-2.0.safetensors [fdcf65e7]",
    "dreamshaper_8.safetensors [9d40847d]",
    "edgeOfRealism_eorV20.safetensors [3ed5de15]",
    "elldreths-vivid-mix.safetensors [342d9d26]",
    "epicrealism_naturalSinRC1VAE.safetensors [90a4c676]",
    "juggernaut_aftermath.safetensors [5e20c455]",
    "lyriel_v16.safetensors [68fceea2]",
    "meinamix_meinaV11.safetensors [b56ce717]",
    "openjourney_V4.ckpt [ca2f377f]",
    "protogenx34.safetensors [5896f8d5]",
    "Realistic_Vision_V5.0.safetensors [614d1063]",
    "redshift_diffusion-V10.safetensors [1400e684]",
    "rundiffusionFX25D_v10.safetensors [cd12b0ee]",
    "rundiffusionFX_v10.safetensors [cd4e694d]",
    "v1-5-pruned-emaonly.safetensors [d7049739]",
    "shoninsBeautiful_v10.safetensors [25d8c546]",
    "theallys-mix-ii-churned.safetensors [5d9225a4]",
    "timeless-1.0.ckpt [7c4971d4]",
    "toonyou_beta6.safetensors [980f6b15]"
]

style_presets = [
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "digital-art",
    "enhance",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
    "texture",
    "craft-clay"
]

# Перевод названий моделей и стилей на русский язык
models_translation = {
    "absolutereality_v181.safetensors [3d9d4d2b]": "Абсолютная реальность v1.81",
    "anything-v4.5-pruned.ckpt [65745d25]": "Что угодно v4.5",
    "AOM3A3_orangemixs.safetensors [9600da17]": "Апельсиновый микс",
    "deliberate_v2.safetensors [10ec4b29]": "Осознанный v2",
    "dreamlike-photoreal-2.0.safetensors [fdcf65e7]": "Фотореализм мечты 2.0",
    "dreamshaper_8.safetensors [9d40847d]": "Мечтатель 8",
    "edgeOfRealism_eorV20.safetensors [3ed5de15]": "Край реализма v2.0",
    "elldreths-vivid-mix.safetensors [342d9d26]": "Яркий микс Эллдрета",
    "epicrealism_naturalSinRC1VAE.safetensors [90a4c676]": "Эпический реализм",
    "juggernaut_aftermath.safetensors [5e20c455]": "Джаггернаут: Послевкусие",
    "lyriel_v16.safetensors [68fceea2]": "Лириэль v1.6",
    "meinamix_meinaV11.safetensors [b56ce717]": "Мейна v11",
    "openjourney_V4.ckpt [ca2f377f]": "Открытый путь v4",
    "protogenx34.safetensors [5896f8d5]": "Протоген x34",
    "Realistic_Vision_V5.0.safetensors [614d1063]": "Реалистичное видение v5.0",
    "redshift_diffusion-V10.safetensors [1400e684]": "Красное смещение v10",
    "rundiffusionFX25D_v10.safetensors [cd12b0ee]": "Рандиффузия FX 2.5D v10",
    "rundiffusionFX_v10.safetensors [cd4e694d]": "Рандиффузия FX v10",
    "v1-5-pruned-emaonly.safetensors [d7049739]": "v1.5 обрезанный",
    "shoninsBeautiful_v10.safetensors [25d8c546]": "Шонин: Красота v10",
    "theallys-mix-ii-churned.safetensors [5d9225a4]": "Микс Аллиса II",
    "timeless-1.0.ckpt [7c4971d4]": "Бессмертный v1.0",
    "toonyou_beta6.safetensors [980f6b15]": "Тунун: Бета 6"
}

style_presets_translation = {
    "3d-model": "3D модель",
    "analog-film": "Аналоговая пленка",
    "anime": "Аниме",
    "cinematic": "Кинематографический",
    "comic-book": "Комикс",
    "digital-art": "Цифровое искусство",
    "enhance": "Улучшение",
    "fantasy-art": "Фантастическое искусство",
    "isometric": "Изометрический",
    "line-art": "Линейный рисунок",
    "low-poly": "Низкополигональный",
    "neon-punk": "Неоновый панк",
    "origami": "Оригами",
    "photographic": "Фотографический",
    "pixel-art": "Пиксель-арт",
    "texture": "Текстура",
    "craft-clay": "Керамическая глина"
}

# Переводчик
translator = Translator()

# Хранение выбранных параметров для каждого пользователя
user_params = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я могу найти информацию в интернете по вашему запросу. Просто напишите тему, которую хотите найти.")

@bot.message_handler(func=lambda message: True)
def search_and_summarize(message):
    query = message.text
    
    # Поиск информации с помощью Google Search API
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={cse_id}"
    response = requests.get(search_url)
    search_results = response.json()
    
    if 'items' in search_results:
        snippets = []
        for item in search_results['items'][:5]:  # Берем первые 5 результатов
            url = item['link']
            page_content = get_page_content(url)
            if page_content:
                snippets.append(page_content)
        
        snippets_text = "\n\n".join(snippets)
        
        # Обработка результатов с помощью OpenAI через openrouter.ai
        prompt = f"Ассистент должен находить в интернете последние новости, связанные с целевой аудиторией - мамами. Основной фокус на новости, касающиеся важности раннего обучения детей арифметике, скорочтению и другим предметам:\n\n{snippets_text}"
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            headers={
                "HTTP-Referer": "https://your-site-url.com",  
                "X-Title": "Your App Name"  
            },
        )
        
        reply = response.choices[0].message.content.strip()
        bot.reply_to(message, reply)
        
        # Генерация текста для блога
        blog_prompt = f"Make sure to provide a detailed and clear overview, ensuring the information is understandable for everyone. Use straightforward and accessible language. Respond in the same language as the user's request. At the end of your response, please include the sources of the information you gathered.:\n\n{reply}"
        blog_response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": blog_prompt}
            ],
            headers={
                "HTTP-Referer": "https://your-site-url.com",  
                "X-Title": "Your App Name" 
            },
        )
        
        blog_text = blog_response.choices[0].message.content.strip()
        
        # Генерация текста для изображения
        image_prompt = f"Выделите основную мысль или лозунг из следующего текста для создания изображения:\n\n{blog_text}"
        image_response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": image_prompt}
            ],
            headers={
                "HTTP-Referer": "https://your-site-url.com",  
                "X-Title": "Your App Name"  
            },
        )
        
        image_text = image_response.choices[0].message.content.strip()
        
        # Генерация изображения
        generate_image(image_text, message.chat.id, {
            "model": "absolutereality_v181.safetensors [3d9d4d2b]",
            "style_preset": "photographic",
            "width": 512,
            "height": 512
        })
        
        # Сохранение результатов
        save_results(blog_text, image_text)
    else:
        bot.reply_to(message, "К сожалению, по вашему запросу ничего не найдено.")

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Извлекаем основной контент, например, все текстовые блоки
        content = ' '.join([p.get_text() for p in soup.find_all('p')])
        return content
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке страницы {url}: {e}")
        return None

def save_results(blog_text, image_prompt):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # Сохранение текста для блога в Word документ
    doc = Document()
    doc.add_paragraph(blog_text)
    doc.save(os.path.join(desktop_path, "blog_text.docx"))

    # Сохранение промпта для изображения в текстовый файл
    with open(os.path.join(desktop_path, "image_prompt.txt"), "w") as f:
        f.write(image_prompt)

def generate_image(prompt, chat_id, params):
    url = "https://api.prodia.com/v1/sd/generate"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": prodia_api_key
    }
    translated_prompt = translator.translate(prompt, src='ru', dest='en').text
    payload = {
        "model": params["model"],
        "prompt": translated_prompt,
        "negative_prompt": "badly drawn",
        "style_preset": params["style_preset"],
        "steps": 20,
        "cfg_scale": 7,
        "seed": -1,
        "upscale": True,
        "sampler": "DPM++ 2M Karras",
        "width": params["width"],
        "height": params["height"]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        response_data = response.json()
        logger.info(f"Ответ от Prodia: {response_data}")  # Логирование ответа от Prodia

        job_id = response_data.get("job")
        if job_id:
            check_job_status(job_id, chat_id)
        else:
            bot.send_message(chat_id, "Ошибка: Job ID не найден в ответе от Prodia.")
            logger.error("Job ID не найден в ответе от Prodia.")
    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, f"Ошибка при генерации изображения: {e}")
        logger.error(f"Ошибка при генерации изображения: {e}")

def check_job_status(job_id, chat_id):
    url = f"https://api.prodia.com/v1/job/{job_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": prodia_api_key
    }
    waiting_msg = bot.send_message(chat_id, "⏳")
    start_time = time.time()
    while time.time() - start_time < 120:  # 2 минуты
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверка на ошибки HTTP
            response_data = response.json()
            logger.info(f"Статус задачи от Prodia: {response_data}")  # Логирование статуса задачи

            status = response_data.get("status")
            if status == "succeeded":
                image_url = response_data.get("imageUrl")
                if image_url:
                    bot.delete_message(chat_id, waiting_msg.message_id)
                    send_image_by_url(chat_id, image_url)
                    return
                else:
                    bot.send_message(chat_id, "Ошибка: URL изображения не найден в ответе от Prodia.")
                    logger.error("URL изображения не найден в ответе от Prodia.")
                    return
            elif status == "failed":
                bot.send_message(chat_id, "Ошибка: Задача завершилась с ошибкой.")
                logger.error("Задача завершилась с ошибкой.")
                return
            else:
                time.sleep(5)  # Подождать 5 секунд перед следующей проверкой
        except requests.exceptions.RequestException as e:
            bot.send_message(chat_id, f"Ошибка при проверке статуса задачи: {e}")
            logger.error(f"Ошибка при проверке статуса задачи: {e}")
            return
        except json.JSONDecodeError as e:
            bot.send_message(chat_id, "Ошибка: Не удалось декодировать JSON ответ от Prodia.")
            logger.error(f"Ошибка при декодировании JSON ответа от Prodia: {e}")
            return

    bot.send_message(chat_id, "Ошибка: Превышено время ожидания. Попробуйте снова.")
    logger.error("Превышено время ожидания.")

def send_image_by_url(chat_id, image_url):
    try:
        # Загрузка изображения по URL
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Проверка на ошибки HTTP

        # Сохранение изображения
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        with open(os.path.join(desktop_path, "image.png"), "wb") as f:
            f.write(image_response.content)

        # Отправка изображения через Telegram API
        bot.send_photo(chat_id, image_response.content)
    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, f"Ошибка при загрузке изображения: {e}")
        logger.error(f"Ошибка при загрузке изображения: {e}")

# Запуск бота
bot.polling()
