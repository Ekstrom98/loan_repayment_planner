import streamlit as st
import requests
from streamlit_lottie import st_lottie
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from functions import *

st.set_page_config(page_title="Lånekoll", page_icon=":tada:", layout="wide")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
 
# ---- LOAD ASSETS ----
lottie_animation = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_OdVhgq.json")

# ---- HEADER SECTION ----
with st.container():
    st.title("Betalningsplan för lån")
    st_lottie(lottie_animation, height = 200, key="money")
    st.write("Uppdateringar påväg:")
    st.write("- Generera PDF som sammanställer din avbetalningsplan.")
    st.write("- Möjlighet att lägga till fler lån.")
    st.write("- Möjlighet att lägga till fler inkomstkällor.")
# ---- PARAMETERS ----
with st.container():
    st.write("---") # Add dividing line from container above
    left_column, right_column = st.columns(2)
    # ---- INCOME ----
    with left_column:
        st.header("Inkomst (SEK)")
        salary = st.number_input("Lön (brutto)", step = 500, min_value = 0)
        tax = st.number_input("Skatt (%)", step = 1, min_value = 0)
        net_salary_header = salary * (1-tax/100)
        st.subheader("= " + str(round(net_salary_header)) + " SEK (netto)")
    # ---- LOAN ----
    with right_column:
        st.header("Lån")
        bank_loan = st.number_input("Banklån (SEK)", step = 100000, min_value = 0)
        down_payment = st.number_input("Kontantinsats", step = 10000, min_value = 0)
        down_payment_start = down_payment
        amortization_rate = st.number_input("Amortering (%)", step = 0.01, min_value = 0.0)
        interest_rate = st.number_input("Ränta (%)", step = 0.01, min_value = 0.0)
        other_loan = st.number_input("Övrigt lån (SEK)", step = 10000, min_value = 0)
        payback_other = st.number_input("Övrig återbetalning per månad (SEK)", step = 500, min_value = 0) 

# ---- TIME ---- 
with st.container():
    st.write("---")
    st.header("Grafer")
    left_column, right_column = st.columns(2)
    with left_column:
        start_date = st.date_input("Startdatum för återbetalning",datetime.date(2022, 1, 1))
    with right_column:
        months_overview = st.slider("Hur många månader framåt vill du se?", 1, 120,12)

# ---- DATA ---- 
data = dataframe_creation(bank_loan = bank_loan, down_payment = down_payment, other_loan = other_loan, 
                   amortization_rate = amortization_rate, interest_rate = interest_rate,
                   payback_other = payback_other, salary = salary, tax = tax, months_overview = months_overview, 
                   start_date = start_date)

# ---- GRAPHS ---- 
with st.container():
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Totalt avbetalt")
        totalt_betalt_df = data[['date', 'total_payed']]
        fig_totalt_betalt = px.line(totalt_betalt_df, x="date", y="total_payed")
        st.plotly_chart(fig_totalt_betalt, use_container_width=True)

        #plt.style.use('ggplot')
        #fig, ax = plt.subplots(1,1,figsize=(7,7), sharex=True, sharey=True)
        #ax.plot(data["date"], data["total_payed"], marker = '', linestyle = '--', color ='black')
        #ax.set_ylabel("SEK")
        #ax.set_xlabel("År")
        #plt.title("Totalt Betalt")
        #plt.savefig('')

    with middle_column:
        st.subheader("Kvar av banklån")
        lån_df = data[['date', 'bank_loan']]
        fig_lån_df = px.line(lån_df, x="date", y="bank_loan")
        st.plotly_chart(fig_lån_df, use_container_width=True)
    
    with right_column:
        st.subheader("Kvar av övriga lån")
        other_loan_df = data[['date', 'other_loan']]
        fig_other_loan_df = px.line(other_loan_df, x="date", y="other_loan")
        st.plotly_chart(fig_other_loan_df, use_container_width=True)

with st.container():
    last_date_string = str(pd.to_datetime(data.loc[0,'date'] + pd.DateOffset(months=months_overview)).to_period('M'))
    st.subheader("Ägarandelar efter " + str(months_overview) + " månader (" + last_date_string + ")")
    
    ownership = (data["total_payed"].iloc[-1] / 2800000) * 100
    not_owned = (1 - data[ "total_payed"].iloc[-1] / 2800000) * 100
    asfig = px.pie(values=[ownership, not_owned], names = ['Min andel', 'Andel jag ej äger'], color = ['blue','red'])
    st.plotly_chart(asfig, use_container_width=True)

with st.container():
    st.write("---")
    st.header("Sammanfattning")
    avg_interest = round(data.interest.mean())
    avg_amortization =  round(data.amortization.mean())
    avg_salary_left = round(data.salary_left.mean())
    max_mean_interest_diff = round(data.interest.mean()-data.interest.max())
    max_mean_amortization_diff = str(round(data.amortization.mean()-data.amortization.max()))+ " SEK från maximalt betald amortering"
    
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Genomsnittlig ränta/månad", value = str(avg_interest) + " SEK", delta=str(max_mean_interest_diff) + " SEK från maximalt betald ränta")
    col2.metric(label = "Genomsnittlig amortering/månad", value = str(avg_amortization) + " SEK", delta=max_mean_amortization_diff)
    col3.metric(label = "Genomsnittlig lön kvar/månad", value = str(avg_salary_left) + " SEK")

with st.container():
    total_payed  = str(round(data["total_payed"].iloc[-1])) + " SEK"
    delta_payed = str(round(data["total_payed"].iloc[-1] - down_payment_start)) + " SEK utöver kontantinsats"
    loan_left = str(round(data.bank_loan.min())) + " SEK"
    delta_loan = str(round(data.bank_loan.min() - data.bank_loan.max())) + " SEK avbetalt"

    other_loan_left = str(round(data.other_loan.min())) + " SEK"
    delta_other_loan = str(round(data.other_loan.min()-data.other_loan.max())) + " SEK avbetalt"

    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Totalt betalt", value = total_payed, delta=delta_payed)
    col2.metric(label = "Kvar av banklån", value = loan_left, delta=delta_loan)
    col3.metric(label = "Kvar av övriga lån", value = other_loan_left, delta=delta_other_loan)
