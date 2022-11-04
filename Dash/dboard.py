from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.stattools import pacf
from statsmodels.tsa.stattools import acf
import plotly.graph_objects as go
import numpy as np
import math


app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv('preprocessed_data.csv')
freqs = pd.read_csv('freqs.csv')
psd = pd.read_csv('psd.csv')
tpreds = pd.read_csv('tpreds.csv')
y_test = pd.read_csv('y_test.csv')
tpreds.index = y_test['InvoiceDate']
mapes = pd.read_csv('mapes.csv')
mapes = mapes['0'].tolist()

fig = px.line(df, x='InvoiceDate', y='total price',  title='Online Sales Time Series')


df_acf = acf(df['total price'], nlags=len(df))
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x= np.arange(len(df_acf)),
    y= df_acf,
    name= 'PACF',
    ))
fig2.update_xaxes(rangeslider_visible=True)
fig2.update_layout(
    title="Autocorrelation",
    xaxis_title="Lag",
    yaxis_title="Autocorrelation",
    #     autosize=False,
    #     width=500,
        #  height=500,
    )
# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

fig3 = px.line(x=freqs['0'], y=psd['0'], title='PSD')

fig4 = px.line(x=y_test['InvoiceDate'], y=[y_test['total price'], tpreds['0']])
# fig4.add_scatter(x=tpreds.index, y=tpreds['0'], mode='lines')
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=y_test['InvoiceDate'], y=y_test['total price'],
                    mode='lines',
                    name='True Values'))
fig4.add_trace(go.Scatter(x=tpreds.index, y=tpreds['0'],
                    mode='lines', name='Predicted Values'))

breakdowns = [0]
figs = []

total_horizon = len(y_test)
for i in range(4, 0, -1):
  # print(math.floor((total_horizon) * 1/i))
  breakdowns.append(math.floor((total_horizon) * 1/i))

for j in range(1, len(breakdowns)):
    tfig = go.Figure()
  # print(breakdowns[j-1], breakdowns[j])
    st = breakdowns[j-1]
    en = breakdowns[j]
    tfig.add_trace(go.Scatter(x=y_test['InvoiceDate'][st:en], y=y_test['total price'][st:en],
                    mode='lines',
                    name='True Values'))
    tfig.add_trace(go.Scatter(x=tpreds.index[st:en], y=tpreds['0'][st:en],
                        mode='lines', name='Predicted Values'))
    sectional = "Section " + str(j) + " Horizon | MAPE = " + "{:.3f}".format(mapes[j-1])
    tfig.update_layout(
    title=sectional,
    )
    figs.append(tfig)


app.layout = html.Div(children=[
    html.H1(children='Online Retail Sales Forecasting'),
    html.H2(children='Time Series of Online Retail Sales'),
    dcc.Graph(
        id='total_ts',
        figure=fig
    ),

    html.Div(children=[
    # fig.show()
    html.H2(children='Autocorrelation Plot & PSD'),
    dcc.Graph(id='pacf', figure=fig2, style={'display': 'inline-block'}),

    dcc.Graph(id='psd', figure=fig3, style={'display': 'inline-block'})
    ]),

    html.H2(children='Forecast with best ARIMA Model'),

    dcc.Graph(
        id='finalForecast',
        figure=fig4,
    ),

    html.H2(children='Model Performance on Test Data - Section-wise Horizon'),
    html.Div(children=[
        
        dcc.Graph(id='chunk1', figure=figs[0], style={'display': 'inline-block','width':'300'}),
        dcc.Graph(id='chunk2', figure=figs[1], style={'display': 'inline-block','width':'300'}),
        dcc.Graph(id='chunk3', figure=figs[2], style={'display': 'inline-block','width':'300'}),
        dcc.Graph(id='chunk4', figure=figs[3], style={'display': 'inline-block','width':'300'}),
    ])



   
])



if __name__ == '__main__':
    app.run_server(debug=True)