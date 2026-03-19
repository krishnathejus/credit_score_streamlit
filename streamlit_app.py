import streamlit as st
import requests

st.title("Credit Score Predictor")

st.header("Borrower Details")

loan_amnt = st.number_input("Loan Amount", value=10000)
dti = st.number_input("Debt-to-Income (DTI)", value=15.0)
annual_inc = st.number_input("Annual Income", value=60000)

addr_state = st.selectbox(
    "State",
    ["CA","TX","NY","FL","OH","WA","MA"]
)

delinq_2yrs = st.number_input("Delinquencies (last 2 years)", value=0)

emp_length = st.selectbox(
    "Employment Length",
    ["< 1 year","1 year","2 years","3 years","4 years","5 years",
     "6 years","7 years","8 years","9 years","10+ years"]
)

grade = st.selectbox(
    "Credit Grade",
    ["A","B","C","D","E","F","G"]
)

home_ownership = st.selectbox(
    "Home Ownership",
    ["RENT","OWN","MORTGAGE","OTHER"]
)

inq_last_6mths = st.number_input(
    "Credit Inquiries (last 6 months)",
    value=0
)

int_rate = st.number_input(
    "Interest Rate (%)",
    value=15.0
)

issue_d = st.selectbox(
    "Loan Issue Date",
    ["Dec-2018","Nov-2018","Oct-2018","Sep-2018"]
)

open_acc = st.number_input(
    "Open Credit Accounts",
    value=10
)

purpose = st.selectbox(
    "Loan Purpose",
    [
        "credit_card",
        "debt_consolidation",
        "home_improvement",
        "major_purchase",
        "small_business",
        "car"
    ]
)

revol_util = st.number_input(
    "Revolving Utilization (%)",
    value=40.0
)

term = st.selectbox(
    "Loan Term",
    ["36 months","60 months"]
)


if st.button("Predict"):
    data = {
        "loan_amnt": loan_amnt,
        "dti": dti,
        "annual_inc": annual_inc,
        "addr_state": addr_state,
        "delinq_2yrs": delinq_2yrs,
        "emp_length": emp_length,
        "grade": grade,
        "home_ownership": home_ownership,
        "inq_last_6mths": inq_last_6mths,
        "int_rate": int_rate,
        "issue_d": issue_d,
        "open_acc": open_acc,
        "purpose": purpose,
        "revol_util": revol_util,
        "term": term
    }
    
    response = requests.post(
        "https://credit-score-api-fy83.onrender.com/predict",
        json=data
    )
    
    st.write("Prediction:", response.json())
    
    result = response.json()

    st.write(result)

    if "credit_score" in result:
        st.success(f"Credit Score: {result['credit_score']}")
        st.write(f"Risk Band: {result['risk_band']}")
        st.write(f"PD: {round(result['pd'],3)}")
    else:
        st.error("API response format incorrect")
