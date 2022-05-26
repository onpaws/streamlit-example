from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import numpy as np
import psycopg2
from collections import defaultdict

conn = psycopg2.connect(
    user = st.secrets["ddn"]["username"],
    password = st.secrets["ddn"]["password"],
    host = st.secrets["ddn"]["host"],
    port = st.secrets["ddn"]["port"],
    database = st.secrets["ddn"]["database"],
)

with st.echo(code_location='below'):
    st.title('Public transit in NYC')
    data_load_state = st.text('Loading data...')
    with conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM "paws~nyc"."station-traffic"')
            result = curs.fetchall()
    
    conn.close()
    data_load_state = st.success('Loading data...done!')
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
        ).properties(title="MTA total turnstile act. per week (Jan 2020-May 2022)")
    st.altair_chart(line_chart, use_container_width=True)