import pandas as pd
from datetime import datetime
from dateutil import parser

# convert the time stamps to datetime 
df = pd.read_csv("./Datasets/online_retail_uk_data.csv")
df['InvoiceDate'] = df['InvoiceDate'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

# read in unemployment data and process
unemployment = pd.read_csv('./Datasets/unemployment.csv')
unemployment['Month'] = unemployment['Month'].apply(lambda x: datetime.strptime(x, '%Y %b'))

# merge unemployment and dataset by month
df = pd.merge(df,unemployment, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
                right_on=unemployment['Month'].apply(lambda y: (y.year, y.month)),
                how='left').iloc[:,1:].drop(columns=['Month'], axis=1)

# merge retail spending by month
retail_spending = pd.read_excel('./Datasets/retail_spending.xlsx',sheet_name='ValNSAT', header=4)
retail_spending = retail_spending.drop([0,1])[['Time Period','All Retailing excluding automotive fuel']]
retail_spending['Time Period'] = retail_spending['Time Period'].apply(lambda x: parser.parse(x))
df = pd.merge(df,retail_spending, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
         right_on=retail_spending['Time Period'].apply(lambda y: (y.year, y.month)),
         how='left').iloc[:,1:].drop(columns=['Time Period'], axis=1)
df = df.rename(columns = {'All Retailing excluding automotive fuel': 'Retail Spending Monthly'})


# merge earnings data
earnings = pd.read_csv("./Datasets/earning.csv")
earnings.rename(columns={ "Time": "Month" }, inplace = True)
earnings["Month"] = earnings['Month'].apply(lambda x: datetime.strptime(x, "%b-%y"))

df = pd.merge(df,earnings, left_on=df['InvoiceDate'].apply(lambda x: (x.year, x.month)),
                right_on=earnings['Month'].apply(lambda y: (y.year, y.month)),
                how='left').iloc[:,1:].drop(columns=['Month'], axis=1)

# print(df)

# df.to_excel('debug.xlsx')

ftse = pd.read_csv("./Datasets/FTSE 100 Historical Data.csv")
ftse = ftse[['Date', 'Price']]
ftse["Date"] = ftse['Date'].apply(lambda x: parser.parse(x))
print(ftse)

df = pd.merge(df, ftse, left_on = df['InvoiceDate'].apply(lambda x: (x.year, x.month, x.day)),
                right_on=ftse['Date'].apply(lambda y: (y.year, y.month, y.day)),
                how='left').iloc[:,1:].drop(columns=['Date'], axis=1)

print(df)

df.to_csv('./Datasets/merged_dataset.csv')