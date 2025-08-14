import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def bonus(P, n):
    P *= 12
    if n <= 14:
        if P < 36_000:
            b = 5
        elif P < 60_000:
            b = 15
        elif P < 90_000:
            b = 25
        else:
            b = 35
    elif n < 20:
        if P < 36_000:
            b = 30
        elif P < 60_000:
            b = 40
        elif P < 90_000:
            b = 50
        else:
            b = 60
    else:
        if P < 36_000:
            b = 55
        elif P < 60_000:
            b = 65
        elif P < 90_000:
            b = 75
        else:
            b = 100
    return b/100

def initial_period(P, r, months):
    balance, bal = [], 0
    for m in range(1, months + 1):
        if m <= 18:
            bal += P
        bal *= r
        bal *= (1 - 0.001)
        if m % 3 == 0:
            bal *= (1 - 0.009)
        balance.append(bal)
    return np.array(balance)

def bonus_balance(P, i, months):
    r = max(i + 0.05, 0.09)
    monthly_r = (1 + r) ** (1/12)
    P *= bonus(P, months/12)
    balance, bal = [], 0
    for m in range(1, months + 1):
        if m <= 12:
            bal += P
        bal *= monthly_r
        bal *= (1 - 0.001)
        if m % 3 == 0:
            bal *= (1 - 0.009)
        balance.append(bal)
    return np.array(balance)

def commited_balance(P, r, i, g, months):
    UDI = 8.53
    balance, bal = [], 0
    for m in range(1, months + 1):
        if m <= 18:
            balance.append(0)
            continue
        else:
            bal += P*(g**(m-18))
            bal *= r
            bal -= 15*(UDI*(i**m))
            bal *= (1 - 0.001)
            balance.append(bal)
    return np.array(balance)

def future_values(plan, P, r, n, i, g):
    months = n * 12
    r_annual = r / 100
    monthly_r = (1 + r_annual) ** (1 / 12)
    i = i / 100
    monthly_i = (1 + i) ** (1 / 12)
    g = g / 100
    monthly_g = (1 + g) ** (1 / 12)

    balance_init = initial_period(P, monthly_r, months)
    balance_bonus = bonus_balance(P, i, months)
    balance_commited = commited_balance(P, monthly_r, monthly_i, monthly_g, months)

    initial_balance = balance_init + balance_bonus
    final_balance = initial_balance + balance_commited

    months_array = np.arange(1, months + 1) / 12

    sigma_annual = 0.9517 * r_annual + 0.0759
    sigma_amount = final_balance * sigma_annual

    fig, ax = plt.subplots(figsize=(10, 6))
    plt.ticklabel_format(style='plain', axis='y')
    sns.lineplot(x=months_array, y=final_balance, label='Final balance', ax=ax)
    ax.fill_between(months_array, final_balance - sigma_amount, final_balance + sigma_amount, color='blue', alpha=0.1, label='Confidence Interval')
    ax.set_xlabel("Years")
    ax.set_ylabel("Future Value ($)")
    ax.legend()
    ax.grid(True)

    final_monthly = P * (monthly_g ** (months - 1))
    final_annual = final_monthly * 12
    bonus_pct = bonus(P, n)
    year_marks = [1] + list(range(5, n + 1, 5))
    balances_at_marks = {"Year ${:,.2f}".format(y): final_balance[int(y * 12) - 1] for y in year_marks}

    summary_data = {
        "Plan": [plan],
        "Initial Monthly Contribution": ["${:,.2f}".format(P)],
        "Initial Annual Contribution": ["${:,.2f}".format(P*12)],
        "Final Year Monthly Contribution": ["${:,.2f}".format(final_monthly)],
        "Final Year Annual Contribution": ["${:,.2f}".format(final_annual)],
        "Bonus Percentage": ["Percentage: {:.0%}".format(bonus_pct)], 
        "Bonus Amount": ["${:,.2f}".format(P*12*bonus_pct)],
        **balances_at_marks,
        f"Final Balance (Year {n})": ["${:,.2f}".format(final_balance[-1])]
    }

    df_summary = pd.DataFrame(summary_data).T  # Transpose for 2 columns
    df_summary.columns = ['Value']

    return fig, df_summary

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Allianz Optimaxx Plus Simulator \n by: RPS Wealth Management")

# Sidebars
with st.sidebar:
    plan_max_values = {
        'Optimaxx Plus art. 93': 25000,
        'Optimaxx Plus art. 151': 17000,
        'Optimaxx Plus art. 185': 12500
    }

    plan = st.selectbox('Plan:', list(plan_max_values.keys()))
    P = st.slider('Monthly Contribution', min_value=2500, max_value=plan_max_values[plan], value=2500, step=500)
    r = st.slider('Return Rate (%)', 0.0, 12.0, 6.0, 0.5)
    n = st.slider('Years', 10, 25, 15, 1)
    i = st.slider('Inflation (%)', 1.0, 5.0, 2.0, 0.5)
    g = st.slider('Growth (%)', 0, 10, 0, 1)

# Main and right columns
col1, col2 = st.columns([2, 1])

fig, df_summary = future_values(plan, P, r, n, i, g)

with col1:
    st.pyplot(fig)

with col2:
    st.dataframe(df_summary)
