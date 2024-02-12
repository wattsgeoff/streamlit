import streamlit as st
import pandas as pd

st.write("Hello world")
st.write("Hello world Again")

test = pd.DataFrame({'One':[1,2,3,4,5],'Two':[6,8,7,8,9]})
st.write(test)

test.plot()