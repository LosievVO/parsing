import pymysql
from datetime import datetime
import time

# Импортируем все парсеры
from auchan_parser import get_auchan_data
from mega_parser import get_mega_data
from sezamo_parser import get_sezamo_data

# Настройки подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'db': 'BEREZKA',
    'charset': 'utf8mb4'
}

# Словарь для выбора парсера
PARSERS = {
    'auchan': get_auchan_data,
    'mega': get_mega_data,
    'sezamo': get_sezamo_data
}

def main():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except pymysql.MySQLError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return

    query = """
    SELECT
        t1.url,
        t1.article,
        t1.competitor
    FROM
        parser_url AS t1
    LEFT JOIN
        parsed_products AS t2 ON t1.article = t2.article AND t1.competitor = t2.competitor AND t2.datetime = CURDATE()
    WHERE
        t2.article IS NULL;
    """
    cursor.execute(query)
    urls_to_parse = cursor.fetchall()
    
    print(f"Найдено {len(urls_to_parse)} новых URL для парсинга.")

    for url, article, competitor in urls_to_parse:
        competitor_lower = competitor.lower().strip()
        parser_func = PARSERS.get(competitor_lower)

        if parser_func:
            print(f"Парсинг {url} с помощью парсера для {competitor}...")
            price = parser_func(url)
            now = datetime.now().date()

            if price is not None:
                cursor.execute(
                    "INSERT INTO parsed_products (article, competitor, price, datetime) VALUES (%s, %s, %s, %s)",
                    (article, competitor, price, now)
                )
                conn.commit()
                print(f"  > Сохранено: Артикул {article} - Цена {price}")
            else:
                print(f"  > Данные не получены. Обновление статуса для URL...")
                cursor.execute(
                    "UPDATE parser_url SET status = 'error' WHERE url = %s",
                    (url,)
                )
                conn.commit()
        else:
            print(f"Парсер для конкурента '{competitor}' не найден. Пропуск.")
        
        time.sleep(2)

    cursor.close()
    conn.close()
    print("Парсинг завершен. Данные сохранены в базе данных.")

if __name__ == "__main__":
    main()
