import streamlit as st
import pandas as pd
import krakenex
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import numpy as np

sns.set(color_codes=True)

#https://www.kraken.com/features/api#public-market-data

k = krakenex.API()
trades = ['XBTUSD']
selected_trade = 'XBTUSD'

# ---------- Ticker
def get_ticker_data(selected_trade):
    ret = k.query_public('Ticker', data = { "pair" : selected_trade })
    orig_ticker_df = pd.DataFrame(ret['result']).transpose()
    ticker_df = orig_ticker_df.copy()
    ticker_df.rename(columns={'a':'ask', 'b':'bid', 'c':'last', 'v':'volume', 'p':'w_avg', 't':'numOfTrades', 'l':'low', 'h':'high', 'o':'openning'}, inplace=True)
    ticker_df['todaysLow'] = round(float(ticker_df['low'][0][0]),2)
    ticker_df['last24hLow'] = round(float(ticker_df['low'][0][1]),2)
    ticker_df['todaysHigh'] = round(float(ticker_df['high'][0][0]),2)
    ticker_df['last24hHigh'] = round(float(ticker_df['high'][0][1]),2)
    ticker_df['lastPrice'] = round(float(ticker_df['last'][0][0]),2)
    #ticker_df.drop(['low', 'high'], axis=1)
    return ticker_df

def get_trades_data(selected_trade):
    # -------------- Trades
    ret = k.query_public('Trades', data = { "pair" : selected_trade })
    trades_df = pd.DataFrame(ret['result']['XXBTZUSD'], columns=['price', 'volume', 'time', 'buy_sell', 'market_limit', 'miscellaneous'])
    trades_df['price'] = trades_df['price'].astype(float)
    trades_df['timestamp'] = pd.to_datetime(trades_df['time'], unit='s')

    sells = trades_df[trades_df['buy_sell']=='s']
    buys = trades_df[trades_df['buy_sell']=='b']

    return sells, buys, trades_df

sells, buys, trades_df = get_trades_data(selected_trade)
ticker_df = get_ticker_data(selected_trade)

#df = trades_df[['timestamp','price']].set_index('timestamp')
#st.line_chart(df)
# --------------------------------
language_dict = {
    "pt": [
        "Como você gostaria de ser contatado?",
        ('Email', 'Telefone', 'Celular'),
        f'Últimas Operações - {selected_trade}', 'Compra', 'Venda',
        'Mais alto do dia', 'Mais baixo do dia'
    ],
    "en": [
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone'),
        f'Last Opperations - {selected_trade}', 'Buy', 'Sell',
        "Today's highest:", "Today's lowest:"
    ]
}
## ---------------------------- SIDEBAR --------------------------------

english_version = st.sidebar.radio(label='Language / Idioma', options=('English','Português'))

if english_version == 'English':
    language_key = 'en'
else:
    language_key = 'pt'

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    language_dict[language_key][0],
    language_dict[language_key][1]
)
## --------------------------------- SIDEBAR END ---------------------------


#st.title(language_dict[language_key][2])
#fig, ax = plt.subplots()
#sells.plot(label=language_dict[language_key][3], ax = ax, y = 'price', x='timestamp', figsize=(13,4), marker='o', c='red', ls=':', fillstyle='top')
#buys.plot(label=language_dict[language_key][4], ax = ax, y = 'price', x='timestamp', figsize=(13,4), marker='o', c='green', ls=':', fillstyle='bottom')
#st.pyplot()

st.title(language_dict[language_key][2])

# ------------- altair chart - interactive last prices ------------
alta_plot = alt.Chart(trades_df).mark_line(
    point=True
).encode(
    x='timestamp',
    y= alt.Y('price', scale=alt.Scale(domain=[trades_df.price.min(), trades_df.price.max()])),
    color='buy_sell'
).properties(
    width=800,
    height=400
).configure_axis(
    labelFontSize=15,
    titleFontSize=20
).interactive()

st.altair_chart(alta_plot, use_container_width=True)

# ------------- matplotlib line chart 
st.subheader(f"{language_dict[language_key][6]}: {ticker_df.iloc[0]['todaysLow']} - {language_dict[language_key][5]}: {ticker_df.iloc[0]['todaysHigh']}")

plt.figure(figsize=(16,5))
sns.lineplot(data = trades_df, x='timestamp', y='price', hue='buy_sell', style='buy_sell', markers=True, dashes=True)
plt.title("Last Negotiations")
st.pyplot()

st.subheader(f"Min: {trades_df['price'].min()}  -  Max: {trades_df['price'].max()}")

#Box Plot
td = pd.DataFrame.from_dict(
    {
        'x':[ticker_df.iloc[0]['lastPrice']], 
        'y':[0],
        'xmin':[trades_df['price'].min()], 
        'xmax':[trades_df['price'].max()]
    }
)

plt.figure(figsize=(16,5))
#ax = sns.barplot(x='x', y='y', color='r', data = td)
ax =sns.boxplot(data = trades_df, x='price')#,  ax=ax)
sns.scatterplot(x='x', y='y', color='y', data = td, ax=ax, s=600, label='Last Price')
sns.scatterplot(x='xmin', y='y', color='r', data = td, ax=ax, s=400, label='Min Price')
sns.scatterplot(x='xmax', y='y', color='g', data = td, ax=ax, s=400, label='Max Price')

plt.title("Last Negotiations")
plt.legend()
st.pyplot()

