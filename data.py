import pandas as pd
from datetime import datetime

df = pd.read_csv("consolidated_retail_data.csv")
df['InvoiceDate'] = df['InvoiceDate'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M"))
