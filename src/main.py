import pandas as pd

import src.config
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (
    analyze_cashback,
    find_person_to_person_transactions,
    investment_bank,
    search_transaction_by_mobile_phone,
    search_transactions_by_user_choice,
)
from src.views import main, user_choice

# web сервисов
main_page = main(src.config.input_date_str, user_choice, src.config.api_key_currency, src.config.api_key_stocks)
print(main_page)

# сервисы
cashback_analysis_result = analyze_cashback(src.config.transactions, src.config.year, src.config.month)
investment_bank_result = investment_bank(src.config.transactions, src.config.date, src.config.limit)
search_transactions_by_user_choice_result = search_transactions_by_user_choice(
    src.config.transactions, src.config.search
)
search_transaction_by_mobile_phone_result = search_transaction_by_mobile_phone(src.config.transactions)
find_person_to_person_transactions_result = find_person_to_person_transactions(src.config.transactions)
print(cashback_analysis_result)
print(investment_bank_result)
print(search_transactions_by_user_choice_result)
print(search_transaction_by_mobile_phone_result)
print(find_person_to_person_transactions_result)


# отчёты
df = pd.read_excel(r"../data/operations.xls")
spending_by_category_result = spending_by_category(df, "Супермаркеты", "2020.05.20")
spending_by_weekday_result = spending_by_weekday(df, "2020.05.20")
spending_by_workday_result = spending_by_workday(df, "2020.05.20")
print(spending_by_category_result)
print(spending_by_weekday_result)
print(spending_by_workday_result)