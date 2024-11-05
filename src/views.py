import json
import os
from dotenv import load_dotenv
from typing import Any

from src.utils import (
    filter_transactions_by_date,
    reading_to_file,
    greeting, get_top_5_transaction, get_stocks_cost, get_exchange_rates, get_info_cards,
)

with open(r"../user_setting.json", "r") as file:
    user_choice = json.load(file)
load_dotenv()
api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")
input_date_str = "07.03.2019"


def main(input_date: Any, user_setting: Any, api_key_currency: Any, api_key_stocks: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    path = r"../data/operations_excel.xlsx"
    transactions = reading_to_file(path)
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    cards_data = get_info_cards(filtered_transactions)
    exchange_rates = get_exchange_rates(user_setting["user_currencies"], api_key_currency)
    stocks_cost = get_stocks_cost(user_setting["user_stocks"], api_key_stocks)
    top_transactions = get_top_5_transaction(filtered_transactions)
    greetings = greeting()
    user_data = {
        "greeting": greetings,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "exchange_rates": exchange_rates,
        "stocks": stocks_cost,
    }
    return json.dumps(user_data, ensure_ascii=False, indent=4)
