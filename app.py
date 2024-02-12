import streamlit as st
import pandas as pd
import time

from kraken_ws import *

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to My App! 👋")

st.sidebar.success("Select a page above.")

status_text = st.sidebar.empty()

kws = Kraken_WS()
kws.spread_sub(['SOL/USDT'])
kws.start()
time.sleep(5)

def get_mid(data):
    return (data['bid']*data['bid_size']+data['ask']*data['ask_size'])/(data['bid_size']+data['ask_size'])

for i in range(0,10):
    k_mid = get_mid(kws.spread_data['SOL/USDT'])
    status_text.text(k_mid)
    time.sleep(1)

kws = None
st.button("Re-run")
# st.markdown(
#     """
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )