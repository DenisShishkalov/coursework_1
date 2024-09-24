from datetime import datetime
import pandas as pd
from src.config import file_operations_xlsx


def filtered_transactions_by_date(transactions: list[dict], input_date_str: str) -> list[dict]:
    """Функция, фильтрующая список транзакций по дате"""
    input_date = datetime.strptime(input_date_str, '%d.%m.%Y')
    end_date = input_date



def greeting() -> str:
    """
    Функция, определяющая дату и время, и осуществляет приветсвие исходя из этих данных
    """
    now = datetime.now()
    current_hour = now.hour
    if 6 < current_hour < 10:
        return 'Доброе утро!'
    elif 10 < current_hour < 18:
        return 'Добрый день!'
    elif 18 < current_hour < 22:
        return 'Доброй вечер !'
    else:
        return 'Доброй ночи!'


def reading_to_file(path: str) -> list[dict]:
    """Функция, принимающая путь до excel файла, и возвращающая список словарей с финансовыми операциями"""

    try:
        df = pd.read_excel(path)
        return df.to_dict(orient='records')
    except Exception as e:
        print(f'Возникла ошибка {e}')
        return []


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
            card_info



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
    return top_transactions


