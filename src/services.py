import json
import re

from src.logger import launch_logging
from src.utils import reading_to_file

logger = launch_logging('services', 'logs/services.log')


def search_transfers_to_individuals(transactions: list[dict]) -> str:
    """
     Функция поиска переводов физическим лицам
    """
    try:
        search_pattern = re.compile(r"\b[А-ЯЁ][а-яё]*\s[А-ЯЁ]\.")
        operations_ = []
        for transaction in transactions:
            category = transaction.get('Категория', '')
            description = transaction.get('Описание', '')
            if category == "Переводы" and search_pattern.search(description):
                operations_.append(transaction)
        logger.info('Выполнен поиск транзакций, отправки средств физ лицам')
        return json.dumps(operations_, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'Произошла ошибка{e}')
        logger.error(f'Произошла ошибка{e}')
        return ''
