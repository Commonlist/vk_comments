import requests
import os
import time
import random
import re
import logging
from pyrogram import Client, filters

# Замените вашими значениями
api_id = "api_id"
api_hash = "api_hash"
access_token = "access_token"

# Создайте клиент для взаимодействия с Telegram API
app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Функция для получения комментариев из ВКонтакте
def get_vk_comments(owner_id, post_id, access_token):
    comments = []
    offset = 0
    count = 100
    while True:
        # Запрос комментариев к посту ВКонтакте
        response = requests.get(f"https://api.vk.com/method/wall.getComments?owner_id={owner_id}&post_id={post_id}&access_token={access_token}&v=5.131&count={count}&offset={offset}")
        data = response.json()
        if 'response' in data:
            # Добавление текста комментариев в список
            comments.extend([item['text'] for item in data['response']['items']])
            # Если получено меньше комментариев, чем запрашивалось, выход из цикла
            if len(data['response']['items']) < count:
                break
            offset += count
        else:
            # Обработка ошибки
            print("Error:", data)
            break
    return comments

# Функция для сохранения комментариев в файл
def save_comments_to_file(comments, file_path):
    with open(file_path, "w") as file:
        file.write("\n".join(comments))

# Функция для подготовки отправки файла с комментариями
def prepare_to_send(file_path):
    # Отправка команды для очистки предыдущих данных в чат GPT-бота
    app.send_message("Your_GPT_Bot", "/clear")
    # Сделайте паузу, чтобы дать боту время на обработку
    time.sleep(random.randint(2, 4))
    # Отправка файла с комментариями в чат
    send_comments_to_chat(file_path)

# Функция для отправки файла с комментариями в чат
def send_comments_to_chat(file_path):
    # Задайте подпись к документу
    caption = "Я хочу изучить комментарии к публикации. Проанализируй их и выведи очень кратко основные тезисы о чём общаются комментаторы."
    # Отправка документа в чат с указанной подписью
    app.send_document("Your_GPT_Bot", file_path, caption=caption)

# Обработчик сообщений, содержащих ссылки на посты ВКонтакте
@app.on_message(filters.chat("me") & filters.regex(r"https?://vk\.com/wall(-\d+)_(\d+)"))
def handle_link(client, message):
    # Использование регулярного выражения для извлечения данных из ссылки
    url_match = re.search(r"https?://vk\.com/wall(-\d+)_(\d+)", message.text)
    if url_match:
        # Извлечение owner_id и post_id из ссылки
        owner_id, post_id = url_match.groups()
        logging.info(f"Handling link: owner_id={owner_id}, post_id={post_id}")
        # Получение комментариев к посту
        comments = get_vk_comments(owner_id, post_id, access_token)
        if comments:
            # Укажите путь к файлу для сохранения комментариев
            file_path = os.path.join("/home/your_login/vk_comments", "vk_comments.txt")
            # Сохранение комментариев в файл
            save_comments_to_file(comments, file_path)
            # Подготовка и отправка файла с комментариями
            prepare_to_send(file_path)

# Запуск клиента
app.run()