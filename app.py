import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="Crew Allowance Table V6", layout="wide")

st.title("✈️ Crew Allowance Calculator V6 (TABLE FORMAT)")

uploaded_file = st.file_uploader("Upload ton planning AIMS (tableau horizontal)", type=["pdf"])
allowance_file = st.file_uploader("Upload ton barème indemnités", type=["pdf", "csv"])

HOME_BASE = "CDG"


# ---------------- BARÈME ----------------
def load_allowances(file):
    allowances = {}

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            allowances[row["Pays"]] = float(row["Montant"])
    else:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for line in text.split("\n"):
                    matches = re.findall(r"([A-Za-z\-\(\) ]+)\s+(\d{2,3}) €", line)
                    for country, value in matches:
                        allowances[country.strip()] = float(value)

    return allowances


# ---------------- PARSE TABLE AIMS ----------------
def extract_table(pdf_file):
    tables = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            t = page.extract_table()

            if t:
                df = pd.DataFrame(t)
                tables.append(df)

    if tables:
        return pd.concat(tables, ignore_index=True)

    return pd.DataFrame()


# ---------------- FIND CDG ----------------
def analyze_table(df):

    # flatten table
    all_cells = df.astype(str).values.flatten()

    all_cells = [c for c in all_cells if c and c != "None"]

    # detect if CDG appears
    has_cdg = any(HOME_BASE in c for c in all_cells)

    # detect last column / last day logic
    last_col = df.iloc[:, -1].astype(str)

    last_has_cdg = any(HOME_BASE in str(x) for x in last_col)

    # ---------------- NIGHT STOP LOGIC ----------------
    if last_has_cdg:
        nights = 0
        case = "Cas A (retour CDG -0.5)"
    else:
        nights = 1
        case = "Cas B (night stop)"

    return {
        "Night stop": nights,
        "Règle": case,
        "Analyse CDG fin tableau": last_has_cdg
    }


# ---------------- MAIN ----------------
if uploaded_file and allowance_file:

    allowances = load_allowances(allowance_file)
    df = extract_table(uploaded_file)

    st.subheader("📊 Tableau extrait AIMS")
    st.dataframe(df, use_container_width=True)

    result = analyze_table(df)

    st.subheader("🧠 Résultat")
    st.write(result)

else:
    st.info("Upload ton planning AIMS en tableau horizontal + barème")
