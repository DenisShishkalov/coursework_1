import json
import os
from dotenv import load_dotenv
from typing import Any

from src.utils import (
    filtered_transactions_by_date,
    get_info_cards,
    reading_to_file,
    get_exchange_rate,
    share_price,
    get_top_transaction,
    greeting,
)

with open("../user_settings.json", "r") as file:
    user_choice = json.load(file)
load_dotenv()
api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")
input_date_str = "20.03.2020"


def main(input_date: Any, user_settings: Any, api_key_currency: Any, api_key_stocks: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    path = r"../data/operations.xls"
    transactions = reading_to_file(path)
    filtered_transactions = filtered_transactions_by_date(transactions, input_date)
    cards_data = get_info_cards(filtered_transactions)
    exchange_rates = get_exchange_rate(user_settings["user_currencies"], api_key_currency)
    stocks_cost = share_price(user_settings["user_stocks"], api_key_stocks)
    top_transactions = get_top_transaction(filtered_transactions)
    greetings = greeting()
    user_data = {
        "greeting": greetings,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "exchange_rates": exchange_rates,
        "stocks": stocks_cost,
    }
    return json.dumps(user_data, ensure_ascii=False, indent=4)