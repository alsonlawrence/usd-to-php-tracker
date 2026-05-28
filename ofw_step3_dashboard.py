# ============================================================
# OFW FOREX TRACKER - DASHBOARD
# ============================================================
# This version reads from Aiven cloud database
# so it works on Streamlit Cloud (live public link)
#
# HOW TO RUN LOCALLY:
#   streamlit run ofw_step3_dashboard.py
#
# HOW TO DEPLOY:
#   Push to GitHub → deploy on share.streamlit.io
# ============================================================

import os
import streamlit as st
import mysql.connector
import pandas as pd
import altair as alt
from datetime import date

# For local running — loads password from .env file
# For Streamlit Cloud — loads from st.secrets instead
try:
    from dotenv import load_dotenv
    load_dotenv()
    AIVEN_PASSWORD = os.getenv("AIVEN_PASSWORD")
except:
    AIVEN_PASSWORD = None

# Streamlit Cloud stores secrets differently
# This checks both .env (local) and st.secrets (cloud)
if not AIVEN_PASSWORD:
    try:
        AIVEN_PASSWORD = st.secrets["AIVEN_PASSWORD"]
    except:
        AIVEN_PASSWORD = ""

# ============================================================
# CLOUD DATABASE SETTINGS — Aiven
# ============================================================
DB_CONFIG = {
    "host":     "mysql-2dfcc8e4-alsonlawrence-usd-to-php-tracker.c.aivencloud.com",
    "port":     14992,
    "user":     "avnadmin",
    "password": AIVEN_PASSWORD,
    "database": "defaultdb",
    "ssl_disabled": False
}


# ============================================================
# FUNCTION: Get today's rates from cloud database
# ============================================================
def get_rates():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        sql = """
            SELECT bank_name, usd_buying_rate, usd_selling_rate, scraped_at
            FROM ofw_bank_rates
            WHERE date_recorded = (SELECT MAX(date_recorded) FROM ofw_bank_rates)
            ORDER BY usd_buying_rate DESC
        """
        df = pd.read_sql(sql, connection)
        connection.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


# ============================================================
# FUNCTION: Get full history for chart
# ============================================================
def get_history():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        sql = """
            SELECT date_recorded, bank_name, usd_buying_rate
            FROM ofw_bank_rates
            ORDER BY date_recorded ASC
        """
        df = pd.read_sql(sql, connection)
        connection.close()
        return df
    except:
        return pd.DataFrame()


# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="USD to PHP Tracker",
    page_icon="💱",
    layout="centered"
)

st.title("💱 USD to PHP Tracker")
st.divider()


# ============================================================
# SECTION 1: TODAY'S RATES TABLE
# ============================================================
st.subheader("Today's Rates (USD to PHP)")

df = get_rates()

if not df.empty:

    scraped_time = pd.to_datetime(df["scraped_at"].iloc[0])
    st.caption(f"As of: {scraped_time.strftime('%B %d, %Y %I:%M %p')}")

    best_buying = df["usd_buying_rate"].max()

    display_rows = []
    for _, row in df.iterrows():
        is_best = row["usd_buying_rate"] == best_buying
        bank    = f"👑 {row['bank_name']}" if is_best else row["bank_name"]
        display_rows.append({
            "Bank":          bank,
            "Buying (PHP)":  f"₱ {row['usd_buying_rate']:,.4f}",
            "Selling (PHP)": f"₱ {row['usd_selling_rate']:,.4f}",
        })

    display_df = pd.DataFrame(display_rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    best_bank = df.loc[df["usd_buying_rate"].idxmax(), "bank_name"]
    st.success(f"👑 Best buying rate today: **{best_bank}** at ₱{best_buying:,.4f} per $1")

else:
    st.warning("No data yet. Run ofw_step2_scraper.py first!")


st.divider()


# ============================================================
# SECTION 2: BUYING RATE HISTORY CHART
# ============================================================
st.subheader("Buying Rate History")

history_df = get_history()

if not history_df.empty and len(history_df) > 1:

    max_rate = history_df["usd_buying_rate"].max()
    min_rate = history_df["usd_buying_rate"].min()
    y_min    = round(min_rate - 0.5, 2)
    y_max    = round(max_rate + 0.5, 2)

    chart = alt.Chart(history_df).mark_line().encode(
        x=alt.X("date_recorded:T", title="Date"),
        y=alt.Y("usd_buying_rate:Q",
                title="Buying Rate (PHP)",
                scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.Color("bank_name:N", title="Bank"),
        tooltip=["date_recorded:T", "bank_name:N", "usd_buying_rate:Q"]
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

else:
    st.info("History chart will appear after a few days of data. Check back soon!")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Rates are indicative only. Always confirm with your bank before transacting. "
    f"Last loaded: {date.today()}"
)
