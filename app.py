import streamlit as st
import pandas as pd
import pdfplumber
import re

st.set_page_config(page_title="Crew Allowance XLS", layout="wide")

st.title("✈️ Crew Allowance Calculator (XLS + BARÈME)")

uploaded_file = st.file_uploader("Upload ton planning Excel", type=["xlsx", "xls"])
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


# ---------------- AIRPORT MAP ----------------
AIRPORT_COUNTRY = {
    "CDG": "France", "NCE": "France", "LYS": "France", "NTE": "France",
    "KRK": "Pologne", "RAK": "Maroc", "EDI": "Grande-Bretagne",
    "LTN": "Grande-Bretagne", "LGW": "Grande-Bretagne",
    "SSH": "Égypte", "RBA": "Maroc",
    "LIN": "Italie", "MXP": "Italie", "GOA": "Italie",
    "BUD": "Hongrie", "BEG": "Serbie"
}


# ---------------- ANALYSE EXCEL ----------------
def analyze_excel(df, allowances):

    results = []

    df = df.fillna("").astype(str)

    for col in df.columns:

        col_data = df[col]

        # ignorer colonne vide
        if not any(col_data):
            continue

        cells = col_data.tolist()

        # ---------------- ROUTES ----------------
        routes = []
        for cell in cells:
            match = re.findall(r"([A-Z]{3})-([A-Z]{3})", cell)
            for dep, arr in match:
                routes.append(f"{dep}-{arr}")

        # ---------------- PAYS ----------------
        countries = []
        for cell in cells:
            for airport in AIRPORT_COUNTRY:
                if airport in cell:
                    countries.append(AIRPORT_COUNTRY[airport])

        unique_countries = list(set(countries))

        # ---------------- NIGHT STOP ----------------
        has_cdg = any("CDG" in cell for cell in cells)

        if has_cdg:
            indemnities = 1 - 0.5
            case = "Cas A"
            nights = 0
        else:
            indemnities = 1
            case = "Cas B"
            nights = 1

        # ---------------- TAUX ----------------
        rates = []

        for c in unique_countries:
            for key in allowances:
                if c.lower() in key.lower():
                    rates.append(allowances[key])

        if not rates:
            rates = [177]

        avg_rate = sum(rates) / len(rates)
        total_eur = indemnities * avg_rate

        results.append({
            "Jour": col,
            "Routes": " → ".join(routes),
            "Pays": ", ".join(unique_countries),
            "Night stop": nights,
            "Règle": case,
            "Indemnités": round(indemnities, 2),
            "Taux €": round(avg_rate, 2),
            "Total €": round(total_eur, 2)
        })

    return pd.DataFrame(results)

# ---------------- MAIN ----------------
if uploaded_file and allowance_file:

    df = pd.read_excel(uploaded_file, header=None)
    allowances = load_allowances(allowance_file)

    st.subheader("📊 Planning")
    st.dataframe(df, use_container_width=True)

   df_results = analyze_excel(df, allowances)

st.subheader("📊 Résultat détaillé")
st.dataframe(df_results, use_container_width=True)

st.subheader("💰 Totaux")
st.metric("Total indemnités", round(df_results["Indemnités"].sum(), 2))
st.metric("Total €", f"{round(df_results['Total €'].sum(), 2)} €")

else:
    st.info("Upload ton planning Excel + ton barème")
