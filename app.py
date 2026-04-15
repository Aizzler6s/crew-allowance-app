import streamlit as st
import pandas as pd
from parser import (
    extract_text_from_pdf,
    parse_flights,
    group_by_day,
    compute_night_stops,
    build_dataframe
)

st.set_page_config(page_title="Crew Planning Analyzer")

st.title("✈️ Crew Planning Analyzer")

uploaded_file = st.file_uploader("Upload your planning PDF", type="pdf")

if uploaded_file:

    text = extract_text_from_pdf(uploaded_file)

    flights = parse_flights(text)

    days_data = group_by_day(text, flights)

    days_data = compute_night_stops(days_data)

    df = build_dataframe(days_data)

    st.subheader("📊 Rotations")

    st.dataframe(df)

    total_ns = df["night_stop"].sum()

    st.metric("🌙 Total Night Stops", total_ns)
