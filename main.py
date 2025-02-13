import requests
import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse


def is_shorten_link(url):
    parsed = urlparse(url)

    return parsed.netloc.lower() in {'vk.cc', 'www.vk.cc', 'vk.com', 'www.vk.com'}


def shorten_link(token, url):
    if not token:
        raise ValueError("VK_API_TOKEN не найден в .env")

    if not urlparse(url).scheme:
        url = f"http://{url}"

    response = requests.get(
        "https://api.vk.com/method/utils.getShortLink",
        params={
            "url": url,
            "access_token": token,
            "v": "5.131"
        }
    )

    data = response.json()
    if not response.ok or "error" in data:
        error_msg = data.get("error", {}).get("error_msg", "Unknown error")
        raise requests.exceptions.HTTPError(f"{error_msg} (Code: {data.get('error', {}).get('error_code', 'Unknown')}")

    return data["response"]["short_url"]


def count_clicks(token, short_url):
    parsed = urlparse(short_url)
    link_key = parsed.path.lstrip('/')

    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats",
        params={
            "key": link_key,
            "access_token": token,
            "v": "5.131",
            "interval": "forever"  # Добавляем параметр для получения всей статистики
        }
    )

    data = response.json()
    if not response.ok or "error" in data:
        error_msg = data.get("error", {}).get("error_msg", "Unknown error")
        raise requests.exceptions.HTTPError(f"{error_msg} (Code: {data.get('error', {}).get('error_code', 'Unknown')}")

    total_clicks = sum(
        period.get("clicks", 0)
        for period in data.get("response", {}).get("stats", [])
    )

    return total_clicks


def main():
    load_dotenv()
    token = os.getenv("VK_API_TOKEN")

    try:
        user_input = input("Введите ссылку: ").strip()

        if is_shorten_link(user_input):
            clicks = count_clicks(token, user_input)
            print(f"Общее количество кликов за всё время: {clicks}")
        else:
            short_url = shorten_link(token, user_input)
            print(f"Сокращённая ссылка: {short_url}")

    except requests.exceptions.HTTPError as e:
        print(f"Ошибка API: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
