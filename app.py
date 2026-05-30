import streamlit as st
import os

st.write("Current directory:", os.getcwd())

st.write("Files in root:")
st.write(os.listdir("."))

if os.path.exists("modules"):
    st.write("Files in modules:")
    st.write(os.listdir("modules"))
else:
    st.error("modules folder not found")
