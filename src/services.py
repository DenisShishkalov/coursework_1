import re

from src.config import file_operations_xlsx
from src.utils import reading_to_file


def search_transfers_to_individuals(transactions: list[dict]) -> list[dict]:
    """
     Функция поиска переводов физическим лицам
    """
    search_pattern = re.compile(r"\b[А-ЯЁ][а-яё]*\s[А-ЯЁ]\.")
    operations_ = []
    for transaction in transactions:
        category = transaction.get('Категория')
        description = transaction.get('Описание')
        if category == "Переводы" and search_pattern.search(description):
            operations_.append(transaction)
    return operations_


if __name__ == '__main__':
    print(search_transfers_to_individuals(reading_to_file(file_operations_xlsx)))