import os
from datetime import datetime, timedelta
import pandas as pd
import requests

from src.config import file_operations_xlsx
from src.logger import launch_logging


logger = launch_logging('utils', 'logs/utils.log')


def greeting() -> str:
    """
    Функция, определяющая дату и время, и осуществляет приветсвие исходя из этих данных
    """
    now = datetime.now()
    current_hour = now.hour
    if 6 < current_hour < 10:
        logger.info('Выполнилось приветствие доброе утро')
        return 'Доброе утро!'
    elif 10 < current_hour < 18:
        logger.info('Выполнилось приветствие добрый день')
        return 'Добрый день!'
    elif 18 < current_hour < 22:
        logger.info('Выполнилось приветствие добрый вече')
        return 'Доброй вечер !'
    else:
        logger.info('Выполнилось приветствие доброй ночи!')
        return 'Доброй ночи!'


def reading_to_file(path: str) -> list[dict]:
    """Функция, принимающая путь до excel файла, и возвращающая список словарей с финансовыми операциями"""

    try:
        df = pd.read_excel(path)
        logger.info('Файл открылся в виде списка словарей')
        return df.to_dict(orient='records')
    except Exception as e:
        print(f'Возникла ошибка {e}')
        logger.error(f'Возникла ошибка {e}')
        return []


def filtered_transactions_by_date(transactions: list[dict], input_date_str: str) -> list[dict]:
    """Функция, фильтрующая список транзакций по дате"""
    input_date = datetime.strptime(input_date_str, '%d.%m.%Y')
    end_date = input_date + timedelta(days=1)
    start_date = datetime(end_date.year, end_date.month, 1)

    def conversion_date(date_str: str) -> datetime:
        """Функция преобразования даты из формата строки в формат dt"""
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

    filtered_transaction = [transaction for transaction in transactions if start_date <= conversion_date(transaction,["Дата операции"]) <= end_date]
    logger.info(f'Транзакции отфильтрованы по дате с{start_date} по {end_date}')
    return filtered_transaction


print(filtered_transactions_by_date(reading_to_file(file_operations_xlsx),'10.12.2020'))


def get_info_cards(transactions: list[dict]) -> list[dict]:
    """
    Функция, получающая список словарей с операциями, и возвращающая информацию:
     - последние 4 цифры карты;
     - общая сумма расходов;
     - кешбэк (1 рубль на каждые 100 рублей).
    """
    card_info = {}
    for trans in transactions:
        card_number = trans.get['Номер карты']
        if not card_number or str(card_number).strip().lower() == "nan":
            continue
        amount = trans.get('Сумма операции')
        if card_number not in card_info:
            card_info[card_number] = {'total_spent': 0.0, 'cashback': 0.0}
        if amount < 0:
            card_info[card_number]['total_spent'] += abs(amount)
            cashback_sum = transactions.get('Кэшбэк')


def get_top_transaction(transactions: list[dict]) -> list[dict]:
    """
    Функция, принимающая список транзакций, выводящая 5 с наибольшей суммой операции
    """
    sorted_transactions = sorted(transactions, key=lambda x: abs(float(x['Сумма платежа'])), reverse=True)
    top_transactions = []
    for trans in sorted_transactions[:5]:
        date = datetime.strptime(trans["Дата операции"], "%d.%m.%Y %H:%M:%S").strftime("%d.%m.%Y")
        (top_transactions.append(
            {"date": date,
             'amount': trans["Сумма операции"],
             'category': trans['Категория'],
             'description': trans['Описание']
             })
        )
    logger.info('Функция выделила топ 5 транзакций по сумме платежа')
    return top_transactions


def get_exchange_rate(transactions: dict) -> list[dict]:
    """
    Функция получения курса валют
    """
    API_KEY = os.getenv('API_KEY')
    headers = {'apikey': f'{API_KEY}'}
    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB'

    response = requests.get(url,headers=headers)
    data = response.json()
    return data


def share_price(stock_list: list[str]) -> list[dict[str, [str | int]]]:
    """Функция получающая курс акций"""
    stocks_rate = []
    for stock in stock_list:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={API}"
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            res = response.json()
            date = res["Meta Data"]["3. Last Refreshed"]
            new_dict = {"stock": stock, "price": round(float(res["Time Series (Daily)"][f"{date}"]["2. high"]), 2)}
            stocks_rate.append(new_dict)
        else:
            utils_logger.info("Произошла ощибка")
            print("Произошла ошибка")
    utils_logger.info("Данные по курсу акций успешно получены")
    return stocks_rate