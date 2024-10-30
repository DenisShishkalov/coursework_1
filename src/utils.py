import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests

from src.config import file_operations_xlsx, api_key_currency, api_key_stocks
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

    filtered_transaction = [transaction for transaction in transactions if
                            start_date <= conversion_date(transaction, ["Дата операции"]) <= end_date]
    logger.info(f'Транзакции отфильтрованы по дате с{start_date} по {end_date}')
    return filtered_transaction


def get_info_cards(transactions: list[dict]) -> list[dict]:
    """
    Функция, получающая список словарей с операциями, и возвращающая информацию:
     - последние 4 цифры карты;
     - общая сумма расходов;
     - кешбэк (1 рубль на каждые 100 рублей).
    """
    card_info = {}
    for transaction in transactions:
        card_number = transaction.get['Номер карты']
        if not card_number or str(card_number).strip().lower() == "nan":
            continue
        amount = transaction.get('Сумма операции')
        if card_number not in card_info:
            card_info[card_number] = {'total_spent': 0.0, 'cashback': 0.0}
        if amount < 0:
            card_info[card_number]['total_spent'] += abs(amount)
            cashback = transactions.get('Кэшбэк')
            if transaction['Категория'] != 'Переводы' and transaction['Категория'] != 'Наличные':
                if cashback is not None:
                    cashback_amount = float(cashback)
                    if cashback_amount >= 0:
                        card_info[card_number]['cashback'] = + cashback_amount
                    else:
                        card_info[card_number]['cashback'] += amount * -0.01
                else:
                    card_info[card_number]['cashback'] += amount * -0.01
    logger.info('посчитали сумму кэшбэка  и сумму на карте')
    card_info = []
    for last_digits, info in card_info.items():
        card_info.append(
            {
                'last_digits': last_digits,
                'total_spent': round(info['total_spent'], 2),
                'cashback': round(info['cashback'], 2),
            }
        )
    logger.info('получена информация о кэшбэке и тратам по каждой карте')
    return card_info


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


def share_price(stock_list: list[str]) -> list[dict[str, [str | int]]]:
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
