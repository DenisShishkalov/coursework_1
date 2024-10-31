from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests


from src.logger import launch_logging

logger = launch_logging('utils', 'logs/utils.log')


def greeting() -> str:   # finish
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


def reading_to_file(path: str) -> list[dict]:   # finish
    """Функция, принимающая путь до excel файла, и возвращающая список словарей с финансовыми операциями"""

    try:
        df = pd.read_excel(path)
        logger.info('Файл открылся в виде списка словарей')
        return df.to_dict(orient='records')
    except Exception as e:
        print(f'Возникла ошибка {e}')
        logger.error(f'Возникла ошибка {e}')
        return []


def conversion_date(date_str: str) -> datetime:   # finish
    """Функция переводит дату из формата строки в формат datetime"""
    return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")


def filter_transactions_by_date(transactions: list[dict], input_date_str: str) -> list[dict]:   # finish дата дд.мм.гггг
    """Функция принимает список словарей с транзакциями и дату
    фильтрует транзакции с начала месяца, на который выпадает входящая дата по входящую дату."""
    input_date = datetime.strptime(input_date_str, "%d.%m.%Y")
    end_date = input_date + timedelta(days=1)
    start_date = datetime(end_date.year, end_date.month, 1)
    filtered_transactions = [transaction for transaction in transactions
                             if start_date <= conversion_date(transaction["Дата операции"]) <= end_date
                             ]
    logger.info(f"Все операции отфильтрованы по дате с {start_date} по {end_date}")
    return filtered_transactions


def get_info_cards(transactions: list[dict]) -> list[dict]:   # finish
    """Функция создает словарь с ключоми номеров карт и в значения добавляет сумму трат и сумму кэшбека"""
    card_data = {}
    for transaction in transactions:
        card_number = transaction.get("Номер карты")
        # если поле номер карты пустое операцию пропускаем т.к. не понятно к какой карте привязать трату
        if not card_number or str(card_number).strip().lower() == "nan":
            continue
        amount = float(transaction["Сумма операции"])
        if card_number not in card_data:
            card_data[card_number] = {"total_spent": 0.0, "cashback": 0.0}
        if amount < 0:
            card_data[card_number]["total_spent"] += abs(amount)
            cashback_value = transaction.get("Кэшбэк")

            if transaction["Категория"] != "Переводы" and transaction["Категория"] != "Наличные":

                if cashback_value is not None:
                    cashback_amount = float(cashback_value)
                    if cashback_amount >= 0:
                        card_data[card_number]["cashback"] += cashback_amount
                    else:
                        card_data[card_number]["cashback"] += amount * -0.01
                else:
                    card_data[card_number]["cashback"] += amount * -0.01
    logger.info('посчитали сумму кэшбэка  и сумму на карте')
    cards_data = []
    for last_digits, data in card_data.items():
        cards_data.append(
            {
                "last_digits": last_digits,
                "total_spent": round(data["total_spent"], 2),
                "cashback": round(data["cashback"], 2),
            }
        )
    logger.info('получена информация о кэшбэке и тратам по каждой карте')
    return cards_data


def get_top_5_transaction(transactions: list[dict]) -> list[dict]:   # finish
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


# print(get_top_5_transaction(reading_to_file(r'../data/operations_excel.xlsx')))


def get_exchange_rate(currency: list[str], api_key_currency: Any) -> list[dict]:
    """
    Функция получения курса валют
    """
    exchange_rates = []
    for cur in currency:
        url = f'https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/{currency}'
        response = requests.get(url)
        logger.info('Запрос на курс валют отправлен')
        if response.status_code == 200:
            data = response.json()

            logger.info(f'получен ответ от сервера о курсе валют {data}')

            rub_cost = data['conversion_rates']['RUB']
            exchange_rates.append({'currency': cur, 'rate': rub_cost})
        else:
            print(f"Ошибка: {response.status_code}, {response.text}")
            logger.error(f"Ошибка api запроса {response.status_code}, {response.text}")
            exchange_rates.append({"currency": currency, "rate": None})
    logger.info('Созданы курсы валют')
    return exchange_rates


def share_price(stock_list: list[str], api_key_stocks: Any) -> list[dict[str, [str | int]]]:
    """Функция получающая курс акций"""
    stocks_rate = []
    for stock in stock_list:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={api_key_stocks}"
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            res = response.json()
            date = res["Meta Data"]["3. Last Refreshed"]
            new_dict = {"stock": stock, "price": round(float(res["Time Series (Daily)"][f"{date}"]["2. high"]), 2)}
            stocks_rate.append(new_dict)
        else:
            logger.info("Произошла ощибка")
            print("Произошла ошибка")
    logger.info("Данные по курсу акций успешно получены")
    return stocks_rate
