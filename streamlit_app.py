import streamlit as st
import requests
import time
import joblib
import numpy as np
import pandas as pd
import os
import pickle
# Base directory (VERY IMPORTANT for Render)
BASE_DIR = os.path.dirname(__file__)

# File paths
woe_path = os.path.join(BASE_DIR, "woe_bins.csv")
model_path = os.path.join(BASE_DIR, "credit_logreg_model.pkl")
factor_path = os.path.join(BASE_DIR, "score_factor.pkl")
offset_path = os.path.join(BASE_DIR, "score_offset.pkl")
features_path = os.path.join(BASE_DIR, "model_features.pkl")
scorecard_path = os.path.join(BASE_DIR, "credit_scorecard.csv")

# Load all artifacts
woe_table = pd.read_csv(woe_path)

model = joblib.load(model_path)
Factor = joblib.load(factor_path)
Offset = joblib.load(offset_path)
features = joblib.load(features_path)

scorecard = pd.read_csv(scorecard_path)

# woe_table = pd.read_csv("woe_bins.csv")
# model = joblib.load("credit_logreg_model.pkl")
# Factor = joblib.load("score_factor.pkl")
# Offset = joblib.load("score_offset.pkl")
# features = joblib.load("model_features.pkl")

# scorecard = pd.read_csv("credit_scorecard.csv")

base_score = scorecard[scorecard["VAR_NAME"]=="Base_Score"]["Points"].values[0]

scorecard = scorecard[scorecard["VAR_NAME"]!="Base_Score"]


def get_points(var, value):

    bins = scorecard[scorecard["VAR_NAME"]==var]

    for _, row in bins.iterrows():

        if row["MIN_VALUE"] <= value <= row["MAX_VALUE"]:
            return row["Points"]

    return 0

# -----------------------------
# WOE Transformation Function
# -----------------------------
def apply_woe(df):

    result = pd.DataFrame()

#   for var in woe_table["VAR_NAME"].unique():
    for var in [f.replace("new_","") for f in features]:

        temp = woe_table[woe_table["VAR_NAME"] == var]
        var_type = temp["VAR_TYPE"].iloc[0]

        # ------------------------
        # NUMERIC VARIABLES
        # ------------------------
        if var_type == "Numeric":

            # ensure numeric type
            temp.loc[:, "MIN_VALUE"] = pd.to_numeric(temp["MIN_VALUE"])
            temp.loc[:, "MAX_VALUE"] = pd.to_numeric(temp["MAX_VALUE"])
            if var not in df.columns:
                df[var] = 0

            def map_bin(x):
                for _, row in temp.iterrows():
                    if row["MIN_VALUE"] <= x <= row["MAX_VALUE"]:
                        return row["WOE"]
                return 0

            result["new_" + var] = df[var].astype(float).apply(map_bin)

        # ------------------------
        # CATEGORICAL VARIABLES
        # ------------------------
        else:
            if var not in df.columns:
                df[var] = "Unknown"

            mapping = dict(zip(temp["MIN_VALUE"], temp["WOE"]))

            result["new_" + var] = df[var].map(mapping).fillna(0)

    return result

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
    
    
    
    
    
    # Convert request → dataframe
    df = pd.DataFrame([data])

    # Apply WOE transformation
    df_woe = apply_woe(df)

    # Ensure model feature order
    df_woe = df_woe.reindex(columns=features, fill_value=0)

    # Predict probability of default
    pd_pred = model.predict_proba(df_woe)[:,1][0]
    
    score = base_score
    for var in [f.replace("new_","") for f in features]:

        
        if var not in df.columns:
            continue
            
        bin_table = scorecard[scorecard["VAR_NAME"] == var]

        value = df[var].iloc[0]

        if bin_table["VAR_TYPE"].iloc[0] == "Numeric":

            row = bin_table[
                (pd.to_numeric(bin_table["MIN_VALUE"]) <= value) &
                (value <= pd.to_numeric(bin_table["MAX_VALUE"]))
            ]

        else:

            row = bin_table[bin_table["MIN_VALUE"] == value]

        if len(row) > 0:
            score += row["Points"].values[0]


    risk_band = "Low Risk"
    if score < 550:
        risk_band = "High Risk"
    elif score < 650:
        risk_band = "Medium Risk"
    st.success(f"Credit Score: {int(score)}")
    st.write(f"Risk Band: {risk_band}")
    st.write(f"PD: {round(float(pd_pred),3)}")