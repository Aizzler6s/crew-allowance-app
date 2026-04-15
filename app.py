import streamlit as st
import pandas as pd
from parser import (
    extract_text_from_pdf,
    extract_flights_with_time,
    group_into_days,
    build_dataframe
)

...

if uploaded_file:

    text = extract_text_from_pdf(uploaded_file)

    flights = extract_flights_with_time(text)

    days = group_into_days(flights)

    df = build_dataframe(days)

    st.dataframe(df)

    st.metric("🌙 Night Stops", df["night_stop"].sum())
