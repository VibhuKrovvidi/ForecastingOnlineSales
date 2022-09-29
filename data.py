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

df = df.rename(columns = {'Seasonally Adjusted Real AWE Total Pay (Index numbers 2015=100)': 'Average Wage'})

# merge ftse
ftse = pd.read_csv("./Datasets/FTSE 100 Historical Data.csv")
ftse = ftse[['Date', 'Price']]
ftse = ftse.rename(columns = {'Price': 'FTSE Price'})
ftse["Date"] = ftse['Date'].apply(lambda x: parser.parse(x))

df = pd.merge(df, ftse, left_on = df['InvoiceDate'].apply(lambda x: (x.year, x.month, x.day)),
                right_on=ftse['Date'].apply(lambda y: (y.year, y.month, y.day)),
                how='left').iloc[:,1:].drop(columns=['Date'], axis=1)

# filter out unwanted data
df = df[df['Quantity']>=0] # do not process cancellations/refunds
df = df[df['Invoice'].apply(lambda x: x.isnumeric())] # check invoice code, full numeric represents proper sales
df['total price'] = df['Quantity']*df['Price'] # to get total value of the order

# convert columns to numeric data type accordingly
df['Retail Spending Monthly'] = pd.to_numeric(df['Retail Spending Monthly'])
df['FTSE Price']=df['FTSE Price'].str.replace(',','')
df['FTSE Price'] = pd.to_numeric(df['FTSE Price'])

# Aggregate the data by day. Target variable is sales aggregated by day. Will notice that saturdays and/or holidays have no sales recorded at all
gmv_orders = df.groupby(pd.Grouper(key='InvoiceDate', axis=0, 
                      freq='D')).agg(
    {'Quantity': 'sum', # total orders in one day
    'total price': 'sum',
    'Unemployment Rate': 'mean',
    'Retail Spending Monthly': 'mean',
    'Average Wage': 'mean',
    'FTSE Price': 'mean'
    } # total gross merchandise value (GMV)/sales in one day
)

print(gmv_orders)

# label saturdays and holidays column
zero_sales = gmv_orders[gmv_orders['total price']==0]
holidays = zero_sales.loc[(zero_sales.index.dayofweek != 5) | (zero_sales.index.month == 12) & (zero_sales.index.day >=24) | (zero_sales.index.month == 1) & (zero_sales.index.day <=3)]
holidays = holidays.reset_index()
saturdays = zero_sales[zero_sales.index.dayofweek == 5]
saturdays = saturdays.reset_index()
print("H",holidays)
print("S", saturdays)

gmv_orders = gmv_orders.reset_index()

gmv_orders['Holiday'] = gmv_orders['InvoiceDate'].apply(lambda x: 1 if x in holidays['InvoiceDate'].values else 0)
gmv_orders['Saturday'] = gmv_orders['InvoiceDate'].apply(lambda x: 1 if x in saturdays['InvoiceDate'].values else 0)

# print(gmv_orders)
gmv_orders = gmv_orders.set_index('InvoiceDate')
gmv_orders['FTSE Price'] = gmv_orders['FTSE Price'].interpolate() # linear interpolation of FTSE values
# gmv_orders = gmv_orders.fillna({'Unemployment Rate': gmv_orders.groupby(gmv_orders.index.month)['Unemployment Rate'].transform('mean'),
#                                 'Retail Spending Monthly': gmv_orders.groupby(gmv_orders.index.month)['Retail Spending Monthly'].transform('mean'),
#                                 'Average Wage': gmv_orders.groupby(gmv_orders.index.month)['Average Wage'].transform('mean')})
gmv_orders = gmv_orders.fillna(method="ffill")
gmv_orders = gmv_orders.reset_index()
gmv_orders.to_csv('./Datasets/daily_aggregated_data.csv', index=False)




