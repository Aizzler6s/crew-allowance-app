import streamlit as st
from parser import (
    extract_text_from_pdf,
    extract_flights_with_time,
    group_into_days,
    build_dataframe
)

st.set_page_config(page_title="Crew Planning Analyzer")

st.title("✈️ Crew Planning Analyzer")

uploaded_file = st.file_uploader("Upload your planning PDF", type="pdf")

if uploaded_file is not None:
    uploaded_file.seek(0)

    try:
        # Extract text
        text = extract_text_from_pdf(uploaded_file)

        # Extract flights
        flights = extract_flights_with_time(text)

        if not flights:
            st.error("❌ Aucun vol détecté dans le PDF")
        else:
            # Group into days
            days = group_into_days(flights)

            # Build dataframe
            df = build_dataframe(days)

            st.subheader("📊 Rotations")
            st.dataframe(df, use_container_width=True)

            # Metrics
            total_ns = df["night_stop"].sum()
            st.metric("🌙 Night Stops", total_ns)

    except Exception as e:
        st.error(f"Erreur : {e}")
