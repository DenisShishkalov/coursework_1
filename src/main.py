import pandas as pd
import src
from src.config import api_key_currency, input_date, api_key_stocks
from src.reports import spending_by_category
from src.services import search_transfers_to_individuals
from src.views import main, user_choice


# web
main_page = main(input_date, user_choice, api_key_currency, api_key_stocks)
print(main_page)
#
# # сервис
find_person_to_person_transactions_result = search_transfers_to_individuals(src.config.transactions)
print(find_person_to_person_transactions_result)


# отчёты
df = pd.read_excel(r"../data/operations_excel.xlsx")
spending_by_category_result = spending_by_category(df, "Супермаркеты", "2020.05.20")

print(spending_by_category_result)
