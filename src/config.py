from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

file_transaction_xlsx = DATA_DIR / 'transactions_excel.xlsx'