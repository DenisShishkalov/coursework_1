import os
from dotenv import load_dotenv

from src.utils import reading_to_file

load_dotenv()

api_key_currency = os.getenv('API_KEY_CURRENCY')
api_key_stocks = os.getenv('API_KEY_STOCKS')

input_date = '07.03.2019'

transactions = reading_to_file(r'../data/operations_excel.xlsx')

year = 2020
month = 5
date = '2020.05'
limit = 50
search = 'Перевод'
