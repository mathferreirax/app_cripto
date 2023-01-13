import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import datetime
import json
import yfinance as yf


with open('data.json', 'r') as _json:
    data_string = _json.read()

obj = json.loads(data_string)

crypto_names = obj["crypto_names"]
crypto_symbols = obj["crypto_symbols"]


crypto_dict = dict(zip(crypto_names, crypto_symbols))

crypto_selected = st.selectbox(label = 'Selecione sua cripto:', 
                               options = crypto_dict.keys())




today_date = datetime.datetime.now()
delta_date = datetime.timedelta(days=360)


col1, col2 = st.columns(2)

with col1:

    start_date = st.date_input(label = 'Selecione a data de ínicio:', 
                               value = today_date - delta_date)

with col2:

    final_date = st.date_input(label = 'Selecione a data final:', 
                               value = today_date)


_symbol = crypto_dict[crypto_selected] + '-USD'

df = yf.Ticker(_symbol).history(interval='1d', 
                                start=start_date, 
                                end=final_date)

st.title(f'Valores de {crypto_selected}')
fig = px.line(df, 
              x = df.index, 
              y = 'Close')

st.plotly_chart(fig)


from prophet import Prophet

df_prophet = pd.DataFrame()

df_cut = df.loc[start_date:final_date]['Close']



df_prophet['ds'] = df_cut.index
df_prophet['y'] = df_cut.values

m = Prophet()
m.fit(df_prophet)

prevision_days = st.slider(label = 'Numero de dias', 
                           value = 20, 
                           min_value = 0,
                           max_value = 100)


future = m.make_future_dataframe(periods=prevision_days)
future.tail()

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

df_to_plot = pd.DataFrame(index = forecast['ds'])

df_to_plot['trend_prevision'] = forecast['yhat'].values

df_to_plot['close_price'] = np.nan
df_to_plot['close_price'].loc[start_date:final_date] = df_cut.values

prevision = px.line(df_to_plot)
st.plotly_chart(prevision)