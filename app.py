import streamlit as st
import pdfplumber
import re

st.title("✈️ Crew Allowance FIX (AIMS horizontal REAL)")

uploaded_file = st.file_uploader("Upload AIMS PDF", type=["pdf"])

HOME_BASE = "CDG"


# ---------------- EXTRACT TEXT ----------------
def extract_text(pdf_file):
    text_pages = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_pages.append(text)

    return "\n".join(text_pages)


# ---------------- PARSE DAYS ----------------
def parse_days(text):

    # split by potential day markers (AIMS often uses DD or DD/MM)
    blocks = re.split(r"(\d{2}/\d{2}|\n\d{1,2}\s)", text)

    days = []

    current = ""

    for b in blocks:
        if not b:
            continue

        # detect new day
        if re.match(r"\d{2}/\d{2}", b) or re.match(r"\n\d{1,2}\s", b):
            if current:
                days.append(current)
            current = b
        else:
            current += b

    if current:
        days.append(current)

    return days


# ---------------- DETECT CDG ----------------
def analyze_days(days):

    if not days:
        return {"error": "no data"}

    last_day = days[-1]

    # check CDG presence in last day
    last_has_cdg = HOME_BASE in last_day

    # NIGHT STOP RULE SIMPLE (CORRECT)
    if last_has_cdg:
        nights = 0
        rule = "Cas A (retour CDG -0.5)"
    else:
        nights = 1
        rule = "Cas B (night stop)"

    return {
        "Night stop": nights,
        "Règle": rule,
        "CDG dernier jour": last_has_cdg
    }


# ---------------- MAIN ----------------
if uploaded_file:

    text = extract_text(uploaded_file)

    days = parse_days(text)

    result = analyze_days(days)

    st.subheader("🧠 Résultat")
    st.write(result)

    st.subheader("🔎 DEBUG (jours détectés)")
    st.write(days)

else:
    st.info("Upload ton PDF AIMS")
