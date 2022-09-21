import pandas as pd
from datetime import datetime
from dateutil import parser

# convert the time stamps to datetime 
df = pd.read_csv("online_retail_uk_data.csv")
df['InvoiceDate'] = df['InvoiceDate'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M"))

# read in unemployment data and process
unemployment = pd.read_csv('unemployment.csv')
unemployment['Month'] = unemployment['Month'].apply(lambda x: datetime.strptime(x, '%Y %b'))

# merge unemployment and dataset by month
df = pd.merge(df,unemployment, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
                right_on=unemployment['Month'].apply(lambda y: (y.year, y.month)),
                how='left').iloc[:,1:].drop(columns=['Month'], axis=1)

# merge retail spending by month
retail_spending = pd.read_excel('retail_spending.xlsx',sheet_name='ValNSAT', header=4)
retail_spending = retail_spending.drop([0,1])[['Time Period','All Retailing excluding automotive fuel']]
retail_spending['Time Period'] = retail_spending['Time Period'].apply(lambda x: parser.parse(x))
df = pd.merge(df,retail_spending, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
         right_on=retail_spending['Time Period'].apply(lambda y: (y.year, y.month)),
         how='left').iloc[:,1:].drop(columns=['Time Period'], axis=1)
df = df.rename(columns = {'All Retailing excluding automotive fuel': 'Retail Spending Monthly'})


# merge earnings data
earnings = pd.read_csv("earning.csv")
earnings.rename(columns={ "Time": "Month" }, inplace = True)
earnings["Month"] = earnings['Month'].apply(lambda x: datetime.strptime(x, "%b-%y"))

df = pd.merge(df,earnings, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
                right_on=earnings['Month'].apply(lambda y: (y.year, y.month)),
                how='left').iloc[:,1:].drop(columns=['Month'], axis=1)