from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import numpy as np
import psycopg2
from collections import defaultdict
from datetime import date
from collections import Counter

st.set_page_config(layout="wide", page_title="NYC Public Transit", page_icon=":train:")

conn = psycopg2.connect(
    user = st.secrets["ddn"]["username"],
    password = st.secrets["ddn"]["password"],
    host = st.secrets["ddn"]["host"],
    port = st.secrets["ddn"]["port"],
    database = st.secrets["ddn"]["database"],
)
# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

with row1_1:
    st.title('Public transit in NYC')

with row1_2:
    st.write(
        """
    ##
    Examining how public transit varies over time in New York City.

    Choose a year-over-year month by sliding the slider.
    """
    )


def weeklytotals():
    data_load_state = st.text('Loading data from DDN...')
    with conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM "paws~nyc"."station-traffic"')
            result = curs.fetchall()
    
    data_load_state = st.success('Done!')
    st.write("**How resilient is NYC's Covid recovery?**")

    totals = defaultdict(int)
    for item in result:
        if (item[5] < 1000000):
            totals[item[0]] += item[5]
    
    data = {"DATE": [], "TOTAL": []}
    for k, v in totals.items():
        data['DATE'].append(k)
        data['TOTAL'].append(v)
    
    source = pd.DataFrame.from_dict(data)
    line_chart = alt.Chart(source).mark_line().encode(
            alt.X('DATE:T', title='Time'),
            alt.Y('TOTAL:Q', title='Weekly rides'),
        ).properties(title="MTA total turnstile activity, per week (Jan 2020-May 2022)")
    st.altair_chart(line_chart, use_container_width=True)

    st.write("**As of May 2022, MTA ridership is slightly more than half of pre-pandemic ridership**")

def popularstations(year):
    with conn:
        with conn.cursor() as curs:
            curs.execute(f"""
            SELECT "START_DATE", "STATION", SUM("TOTAL")
            FROM
            (SELECT
                "START_DATE",
                "STATION", 
                "TOTAL"
            FROM
                "paws~nyc"."station-traffic"
            ) s
            WHERE to_date("START_DATE", 'MM/DD/YYYY') BETWEEN '{month}/1/{year}' AND '{month+1}/1/{year}'
            GROUP BY "START_DATE", "STATION"
            """)
            stations_by_date = curs.fetchall()
            
    data = defaultdict(int)
    for i in stations_by_date:
        data[i[1]] += i[2]
    sorted_data = dict(Counter(data).most_common(5))

    print(sorted_data)
    source = pd.DataFrame({
        'Station': [x for x in sorted_data.keys()],
        'Activity': [x for x in sorted_data.values()]
    })

    st.altair_chart(
        alt.Chart(source, title=f"{month}/{year}")
        .mark_bar()
        .encode(
            x=alt.X("Station", scale=alt.Scale(nice=False)),
            y=alt.Y("Activity:Q", scale=alt.Scale(domain=[0, 11000000])),
            tooltip=["Station", "Activity"],
        )
        .configure_mark(opacity=0.2, color="red"),
        use_container_width=True,
    )




weeklytotals()

row2_1, row2_2 = st.columns((1,1))
with row2_1:
    st.write("## Most popular stations year over year")
with row2_2:
    month = st.slider("Choose a month (Jan = 1, Feb = 2, etc)", min_value=1, max_value=5, )
row3_1, row3_2, row3_3 = st.columns((1,1,1))
with row3_1:
    popularstations(2020)
with row3_2:
    popularstations(2021)
with row3_3:
    popularstations(2022)







conn.close()