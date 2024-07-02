import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import requests
import time
import os
#from web3 import Web3

from nixtla import NixtlaClient
nixtla_client = NixtlaClient(
    #api_key = NIXTLA_API_KEY
)
nixtla_client.validate_api_key()

token_dict = pd.read_csv('token_dictionnary.csv')

### Config
st.set_page_config(
    page_title="Walletscan",
    page_icon="👽 ",
    layout="wide"
)

@st.cache_data
def list_holders(token_address):
  url = f'https://walletscan-api-7f80b4b1818a.herokuapp.com/top-holders/{token_address.lower()}'
  response = requests.get(url)

  if response.status_code == 200:
    top_holders = response.json()
    top_holders_data = pd.DataFrame(top_holders)
    if len(top_holders_data) > 0:
      top_holders_data.columns = ['wallet_address','balance']
      top_holders_data['balance'] = top_holders_data['balance'].round()
      top_holders_data['profile'] = top_holders_data['wallet_address'].apply(lambda x: f"https://walletscan-app-8c8ac35cc942.herokuapp.com/?token={token_address}&wallet={x}")
      top_holders_data.set_index('wallet_address', inplace=True)
    return dict({
      'status_code' : 200,
      'top_holders' : top_holders_data
    })
  else:
    return  dict({
      'status_code' : response.status_code,
    })
  
# Create a plotly figure
def display_plot(df,forecast_df,level):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], y=df['balance'], mode='lines', 
            line=dict(color='blue'), name='Actual Value'
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df['timestamp'], y=forecast_df['TimeGPT'], mode='lines', 
            line=dict(color='red'), name='Forecast',
        ),
    )
    lo = forecast_df[f'TimeGPT-lo-{level}'].to_list()
    hi = forecast_df[f'TimeGPT-hi-{level}'].to_list()
    ds = forecast_df['timestamp'].to_list()
    fig.add_trace(
        go.Scatter(
            x=ds + ds[::-1],  # X coordinates for the filled area.
            y=hi + lo[::-1],  # Y coordinates for the filled area.
            fill='toself',  # The area under the trace is filled.
            fillcolor='rgba(0,176,246,0.2)',  # The fill color.
            line_color='rgba(255,255,255,0)',  # The line color.
            #showlegend=False,  # The trace is not added to the legend.
            name='Prediction Interval',
        )
    )
    fig.update_layout(
        #title='Time Series ',#+selected_uid,
        #xaxis_title='Date',
        #yaxis_title='Value',
        margin=dict(l=0, r=0, t=0, b=0),  # Suppression des marges
        yaxis=dict(range=[0, None]),
        legend=dict(
        orientation="h",  # Orientation horizontale
        yanchor="bottom", # Ancrage en bas
        y=1,              # Positionnement au-dessus de la figure
        xanchor="center", # Ancrage au centre
        x=0.5             # Centré horizontalement
    )
    )
    # Show the plot
    #fig.show()
    st.plotly_chart(fig)
   

with st.sidebar:
    with st.form('token_selector'):
      token_input = ''
      if 'token' in st.query_params.keys() :
        token_input = st.query_params.token
      token_address = st.text_input('Token address', value=token_input)
      submitted = st.form_submit_button('List token holders', use_container_width=True)
      #with st.spinner("Loading..."):
      #  time.sleep(2)
      if len(token_address) != 42 :
        st.warning('Token address format must be a 42 character string!', icon='⚠')
        print(st.query_params)
      else :

        data_load_state = st.text('Loading data...')
        response = list_holders(token_address) 
        data_load_state.text("")

        if response['status_code'] == 200:
          top_holders_data = response['top_holders']
          st.dataframe(top_holders_data, 
                       column_config={
                          "profile": st.column_config.LinkColumn(
                              "profile",
                              help="Click to view profile",
                              max_chars=100,
                              display_text="view"
                          ),
                        },
                      use_container_width=True,
                      height=1000
            )
        else:
            st.warning(f"Error: {response['status_code']}", icon='⚠')

@st.cache_data
def get_wallet_info(wallet_address=str):
  url = f'https://walletscan-api-7f80b4b1818a.herokuapp.com/wallet-info/{wallet_address.lower()}'
  response = requests.get(url)
  if response.status_code == 200:
      wallet_info = response.json()
      wallet_data = pd.DataFrame(wallet_info)
      return dict({
         'status_code' : 200,
         'wallet_data' : wallet_data
      })
  else:
      return dict({
         'status_code' : response.status_code,
      })
  
if 'wallet' not in st.query_params.keys() :
  st.warning('Select a user profile', icon='⚠')
elif len(st.query_params.wallet) != 42 :
  st.warning('Wallet address must have 42 characters', icon='⚠')
elif 'token' not in st.query_params.keys() :
  st.warning('Select a token', icon='⚠')
elif len(st.query_params.token) != 42 :
  st.warning('Token address must have 42 characters', icon='⚠')
else:
  token_info = token_dict.loc[token_dict['address'] == st.query_params.token.lower()]
  if len(token_info) > 0:
    st.subheader(f"{token_info.iloc[0]['name']} ({token_info.iloc[0]['symbol']})", divider='rainbow')
  else:
    st.subheader(f"Token: {st.query_params.token[:4]}...{st.query_params.token[-4:]}", divider='rainbow')
  st.text(f"Wallet: {st.query_params.wallet}")

  data_load_state = st.text('Loading data...')
  response = get_wallet_info(st.query_params.wallet)

  def expend_wallet_history(balance_history):
    balance_history['timestamp'] = pd.to_datetime(balance_history['timestamp'])
    dates = pd.date_range(start='2024-01-01', end='2024-04-01', freq='D')
    df = pd.DataFrame(index=dates)
    df = df.merge(token_only, how='left', left_index=True, right_on='timestamp')
    df = df.set_index('timestamp').reindex(dates)
    df['balance'] = df['balance'].ffill().fillna(0)
    df = df.reset_index()
    df = df.rename(columns={'index': 'timestamp'})
    return df
  

  if response['status_code'] == 200:
    df = pd.DataFrame(response['wallet_data'])
    df.drop("wallet_address", axis=1, inplace=True)
    ###
    data_load_state.text("") 
    first_tx = pd.to_datetime(df['timestamp'].min()).year
    last_tx_year = pd.to_datetime(df['timestamp'].max()).year
    last_tx_month = pd.to_datetime(df['timestamp'].max()).month
    nb_unique_tokens = df["token_address"].nunique()
    nb_tx = df['timestamp'].count()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active since", f"{first_tx}")
    col2.metric("Last activity", f"{last_tx_year}/{last_tx_month}")
    col3.metric("Number of tokens", f"{nb_unique_tokens}")
    col4.metric("Number of tx", f"{nb_tx}")
    st.divider()
    col1a, col2a = st.columns(2)
    with col1a:
      col1b, col2b, col3b = st.columns(3)
      col3b.button(":grey[:flag-eu: EU timezone]", type="primary")
      col2b.button(":grey[:game_die: High risk tokens]", type="primary")
      col1b.button(":grey[:whale: Whealty holder]", type="primary")
    st.divider()
    data_load_state = st.text('Loading data...')
    ###
    token_only = df.loc[df['token_address']==st.query_params.token.lower()].copy() # WARNING IF NO TOKEN
    token_only.drop("token_address", axis=1, inplace=True)
    token_only['balance'] = (token_only['balance']/10000).round()
    expended_balance = expend_wallet_history(token_only)

    timegpt_fcst_df = nixtla_client.forecast(df=expended_balance, 
                                            h=12, 
                                            freq='D', 
                                            time_col='timestamp', 
                                            target_col='balance',
                                            level=[80, 90],
                                            #add_history=True,
                                            )
    data_load_state.text("") 
    display_plot(expended_balance,timegpt_fcst_df,90)

    st.divider()
    st.dataframe(
      df.groupby('token_address')['balance'].apply(list),
      column_config={
        "balance": st.column_config.BarChartColumn(
            "balances_history", y_min=0, y_max=500000
          ),
        },
        use_container_width=True,
      )

  else: 
    data_load_state.text("") 
    st.warning(f"Error: {response['status_code']}", icon='⚠') 



