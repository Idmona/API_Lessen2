import requests
import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse


def is_shorten_link(token, url):
    response = requests.get(
        "https://api.vk.com/method/utils.checkLink",
        params={
            "url": url,
            "access_token": token,
            "v": "5.131"
        }
    )

    response.raise_for_status()

    response_json = response.json()
    if "error" in response_json:
        error_msg = response_json["error"].get("error_msg", "Unknown error")
        raise requests.exceptions.HTTPError(
            f"{error_msg} (Code: {response_json['error'].get('error_code', 'Unknown')})")

    return response_json.get("response", {}).get("link_type") == "shortened"


def shorten_link(token, url):
    response = requests.get(
        "https://api.vk.com/method/utils.getShortLink",
        params={
            "url": url,
            "access_token": token,
            "v": "5.131"
        }
    )

    response.raise_for_status()

    response_json = response.json()
    if "error" in response_json:
        error_msg = response_json["error"].get("error_msg", "Unknown error")
        raise requests.exceptions.HTTPError(
            f"{error_msg} (Code: {response_json['error'].get('error_code', 'Unknown')})")

    return response_json["response"]["short_url"]


def count_clicks(token, short_url):
    parsed_url = urlparse(short_url)
    link_key = parsed_url.path.lstrip('/')

    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats",
        params={
            "key": link_key,
            "access_token": token,
            "v": "5.131",
            "interval": "forever"
        }
    )

    response.raise_for_status()

    response_json = response.json()
    if "error" in response_json:
        error_msg = response_json["error"].get("error_msg", "Unknown error")
        raise requests.exceptions.HTTPError(
            f"{error_msg} (Code: {response_json['error'].get('error_code', 'Unknown')})")

    total_clicks = sum(
        period.get("clicks", 0)
        for period in response_json.get("response", {}).get("stats", [])
    )

    return total_clicks


def main():
    load_dotenv()
    token = os.environ["vk_api_token"]

    try:
        user_input = input("Введите ссылку: ").strip()

        if is_shorten_link(token, user_input):
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
