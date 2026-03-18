import streamlit as st
import requests

st.title("Credit Score Predictor")

income = st.number_input("Income")
age = st.number_input("Age")

if st.button("Predict"):
    data = {
        "income": income,
        "age": age
    }
    
    response = requests.post(
        "https://credit-score-api-fy83.onrender.com/predict",
        json=data
    )
    
    st.write("Prediction:", response.json())
