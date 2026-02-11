import requests
from bs4 import BeautifulSoup

def get_auchan_data(url):
    """
    Функция для парсинга данных с сайта auchan.ro
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Сначала пробуем найти цену по новому классу
    price_element = soup.find('span', class_='vtex-product-price-1-x-sellingPriceWithUnit')
    
    # Если не найдено, пробуем найти по старому классу
    if not price_element:
        price_element = soup.find('span', class_='vtex-product-price-1-x-sellingPriceWithUnitMultiplier')

    # Если элемент с ценой найден, извлекаем данные
    if price_element:
        try:
            raw_price = price_element.text.strip()
            price = raw_price.replace(' ', '').replace('lei', '').replace(',', '.').strip()
            price = float(price)
        except (AttributeError, ValueError):
            price = None
    else:
        price = None
    
    return price
