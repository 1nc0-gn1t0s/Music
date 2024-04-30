import json
import requests
import shutil
import base64
from PIL import Image
from io import BytesIO

from models import Song, User, db


headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDliY2Q4YjktNTU0NC00MTliLWI4ZDQtZTAzNjE1YzczMmY5IiwidHlwZSI6ImFwaV90b2tlbiJ9.yTnAFB9H6ntk9EYASNUoMnVv_z3bxNcP145Lr_gGc9k"}


def make_text_path(info: list, user: User):
    """
    Функция для сохранения текста песни в файл
    :param info: информация о песне
    :param user: пользователь
    :return: путь к расположению файла с текстом
    """
    title, text = info[0], info[3]
    file = open(f'{title}_{user.id}.txt', 'w+')
    file.write(text)
    file.close()
    shutil.move(f"{title}_{user.id}.txt", f"static/texts/{title}_{user.id}.txt")
    return f'static/texts/{title}_{user.id}.txt'


def make_text(info: list) -> str:
    """
    Функция для преобразования текста (при его наличии) песни в краткое описание фотографии.
    Если есть описание фотографии от пользователя, то используется оно.
    Если нет ни текста, ни описания фотографии, то используется название песни
    :param info: информация о песне
    :return: текст для описания фотографии
    """
    global headers

    title, song_lyrics, desc = info[0], info[3], info[4]

    if desc:
        return desc

    if song_lyrics:
        url0 = "https://api.edenai.run/v2/text/topic_extraction"

        payload0 = {
            "providers": "google,ibm,openai",
            "language": "en",
            "text": song_lyrics,
            "fallback_providers": ""
        }

        response = requests.post(url0, json=payload0, headers=headers)

        result = json.loads(response.text)
        a = result['google']['items']
        b = ', '.join([a[i]['category'] for i in range(len(a))])

        url1 = "https://api.edenai.run/v2/text/keyword_extraction"

        payload1 = {
            "providers": "amazon,microsoft",
            "language": "en",
            "text": song_lyrics,
            "fallback_providers": ""
        }

        response = requests.post(url1, json=payload1, headers=headers)

        result = json.loads(response.text)
        n = result['amazon']['items']
        m = ', '.join([a[i]['category'] for i in range(len(n))])

        return b + m
    return title


def add_song(title: str, singer: str, filepath: str, text_path: str, photo_path: str, user: User) -> None:
    """
    Функция для добавления новой песни в базу данных
    :param title: название песни
    :param singer: исполнитель
    :param filepath: путь к песне
    :param text_path: путь к файлу с текстом песни
    :param photo_path: путь к файлу с фото песни
    :param user: пользователь
    :return: None
    """
    song = Song(title, singer, text_path, filepath, photo_path, user.id)
    db.session.add(song)
    db.session.commit()


def make_cover(info: list, user: User) -> str:
    """
    Функция для создания обложки для песни
    :param info: информация о песне
    :param user: пользователь
    :return: путь к обложке для песни
    """
    global headers

    title = info[0]
    text = make_text(info)

    url = "https://api.edenai.run/v2/image/generation"
    payload = {
        "providers": "openai",
        "text": text,
        "resolution": "256x256",
        "fallback_providers": "dall-e-3"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    data = result['openai']['items']['image']
    im = Image.open(BytesIO(base64.b64decode(data)))
    im.save(f'{title}_{user.id}.png', 'PNG')

    return f'{title}_{user.id}.png'
