import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align:center'>AI Powered SAR Dashboard</h1>", unsafe_allow_html=True)

st.subheader("Upload Transaction CSV")
file = st.file_uploader("Upload CSV file", type=["csv"])

# ================= MAIN APP =================
if file is not None:

    # Read CSV
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # -------- Detect Date Column --------
    possible_names = ["date","time","timestamp","txn_date","transaction_date"]

    date_col = None
    for col in df.columns:
        if col.lower() in possible_names:
            date_col = col
            break

    if date_col is None:
        st.warning("Date column not detected automatically")
        date_col = st.selectbox("Select Date Column", df.columns)

    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except:
        st.error("Selected column cannot be converted to date")
        st.stop()

    # -------- Validate Required Columns --------
    required_cols = ["Amount", "Type"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    # -------- Show Table --------
    st.subheader("Transaction Data")
    st.dataframe(df, use_container_width=True)

    # -------- Basic Calculations --------
    total = df["Amount"].sum()
    avg = df["Amount"].mean()
    max_amt = df["Amount"].max()
    min_amt = df["Amount"].min()
    std_dev = df["Amount"].std()
    txn_count = len(df)

    col1, col2 = st.columns(2)

    # -------- Summary --------
    with col1:
        st.subheader("Summary")
        st.write("Total:", round(total,2))
        st.write("Average:", round(avg, 2))
        st.write("Maximum:", max_amt)
        st.write("Minimum:", min_amt)
        st.write("Transaction Count:", txn_count)

    # -------- ADVANCED RISK SCORE --------
    with col2:

        # ---- Outlier Score (Z-score based) ----
        if std_dev == 0:
            outlier_score = 0
        else:
            outlier_score = (max_amt - avg) / std_dev

        outlier_score = min(outlier_score * 5, 40)

        # ---- Volatility Score ----
        volatility_score = min((std_dev / avg) * 20 if avg != 0 else 0, 20)

        # ---- Deposit vs Withdrawal Imbalance ----
        type_sum = df.groupby("Type")["Amount"].sum()
        deposit = type_sum.get("Deposit", 0)
        withdraw = type_sum.get("Withdrawal", 0)

        if (deposit + withdraw) == 0:
            imbalance_score = 0
        else:
            imbalance_ratio = abs(deposit - withdraw) / (deposit + withdraw)
            imbalance_score = imbalance_ratio * 20

        # ---- Frequency Score ----
        frequency_score = min(txn_count / 5, 20)

        # ---- Final Risk Score ----
        risk_score = outlier_score + volatility_score + imbalance_score + frequency_score
        risk_score = round(min(risk_score, 100), 2)

        st.subheader("Risk Score")
        st.markdown(f"<h1 style='text-align:center'>{risk_score}</h1>", unsafe_allow_html=True)

        if risk_score >= 60:
            st.error("High Risk Account")
        elif risk_score >= 40:
            st.warning("Medium Risk Account")
        else:
            st.success("Low Risk Account")

    # -------- Narrative --------
    st.subheader("SAR Narrative")

    narrative = f"""
Customer transaction analysis indicates the following:

• Average Transaction: {round(avg,2)}
• Maximum Transaction: {max_amt}
• Standard Deviation: {round(std_dev,2)}
• Transaction Count: {txn_count}
• Final Risk Score: {risk_score}

The system detected outlier activity, volatility, and behavioral imbalance.
Further investigation is recommended based on calculated risk metrics.
"""
    st.write(narrative)

    # -------- Graphs --------
    col3, col4, col5 = st.columns(3)

    # Trend Graph
    with col3:
        st.subheader("Transaction Trend")
        fig1 = plt.figure()
        plt.plot(df[date_col], df["Amount"], marker="o")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1)

    # Bar Graph
    with col4:
        st.subheader("Deposit vs Withdrawal")
        fig2 = plt.figure()
        type_sum.plot(kind="bar")
        plt.tight_layout()
        st.pyplot(fig2)

    # Pie Chart
    with col5:
        st.subheader("Transaction Distribution")
        fig3 = plt.figure()
        type_sum.plot(kind="pie", autopct="%1.0f%%")
        plt.ylabel("")
        plt.tight_layout()
        st.pyplot(fig3)

    # -------- Save Audit --------
    audit = {
        "date": str(datetime.datetime.now()),
        "risk_score": float(risk_score),
        "total": float(total),
        "transactions": int(txn_count)
    }

    with open("audit.json", "a") as f:
        json.dump(audit, f)
        f.write("\n")

    st.success("Audit Saved")