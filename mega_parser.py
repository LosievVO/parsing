import requests
from bs4 import BeautifulSoup

def get_mega_data(url):
    """
    Функция для парсинга данных с сайта mega-image.ro
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим основную часть цены (целые числа)
    try:
        # Используем div и class, который вы указали
        price_main_element = soup.find('div', class_='sc-dqia0p-9 jWCjCP')
        price_main = price_main_element.text.strip()
    except AttributeError:
        price_main = None

    # Находим дробную часть цены (значения после запятой)
    try:
        # Используем sup и class, который вы указали
        price_decimal_element = soup.find('sup', class_='sc-dqia0p-10 cNzomO')
        price_decimal = price_decimal_element.text.strip()
    except AttributeError:
        price_decimal = "00"

    # Объединяем части и преобразуем в число
    if price_main is not None:
        full_price_str = f"{price_main},{price_decimal}"
        price = float(full_price_str.replace(',', '.'))
    else:
        price = None

    return price
