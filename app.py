import streamlit as st
from st_paywall import add_auth
import random
st.set_page_config(layout="wide")
st.title("Welcome to Assistit")

add_auth(required=True)
with st.sidebar:

    st.write(f"Subscription status:{st.session_state.user_subscribed}")
    st.write(f"{st.session_state.email}")

"""
You are in Welcome to the house
"""
@st.experimental_fragment(run_every=3)
def fragment():
    "this will happen every 3 seconds"


st.text_area("Enter your text here")
fragment()



