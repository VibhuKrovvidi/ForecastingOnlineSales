import pandas as pd
df1 = pd.read_excel('online_retail_II.xlsx',sheet_name='Year 2009-2010')
df2 = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2010-2011')
df = pd.concat([df1,df2], axis=0)
uk = df[df['Country']=='United Kingdom']
uk.to_csv('online_retail_uk_data.csv', index=False)
print('CSV outputted')