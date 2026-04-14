import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Crew Allowance Calculator V4", layout="wide")

st.title("✈️ Crew Allowance Calculator V4 (LAYOVER INTELLIGENT)")

uploaded_file = st.file_uploader("Upload ton planning AIMS", type=["pdf"])
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


# ---------------- PARSE AIMS ----------------
def extract_flights(pdf_file):
    flights = []
    current_date = None

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):

                date_match = re.match(r"(\d{2}/\d{2}/\d{4})", line)
                if date_match:
                    current_date = datetime.strptime(date_match.group(1), "%d/%m/%Y").date()

                routes = re.findall(r"([A-Z]{3})\s+-\s+([A-Z]{3})", line)
                times = re.findall(r"A?(\d{2}:\d{2})", line)

                for i, (dep, arr) in enumerate(routes):
                    dep_time = times[i * 2] if len(times) > i * 2 else None
                    arr_time = times[i * 2 + 1] if len(times) > i * 2 + 1 else None

                    flights.append({
                        "date": current_date,
                        "dep": dep,
                        "arr": arr,
                        "dep_time": dep_time,
                        "arr_time": arr_time
                    })

    return flights


# ---------------- ROTATIONS ----------------
def build_rotations(flights):
    rotations = []
    current = []

    for f in flights:
        current.append(f)

        if f["arr"] == HOME_BASE:
            rotations.append(current)
            current = []

    if current:
        rotations.append(current)

    return rotations


# ---------------- LAYOVER DETECTION ----------------
def detect_layover_type(f, next_f):

    # sécurité
    if not f["date"] or not next_f["date"]:
        return "TRANSIT"

    # build datetime si possible
    if f["arr_time"] and next_f["dep_time"]:
        t1 = datetime.combine(
            f["date"],
            datetime.strptime(f["arr_time"], "%H:%M").time()
        )

        t2 = datetime.combine(
            next_f["date"],
            datetime.strptime(next_f["dep_time"], "%H:%M").time()
        )

        hours = (t2 - t1).total_seconds() / 3600

        if hours <= 6:
            return "TRANSIT"
        else:
            return "LAYOVER_HOTEL"

    # fallback jour
    if (next_f["date"] - f["date"]).days >= 1:
        return "LAYOVER_HOTEL"

    return "TRANSIT"


# ---------------- ANALYSIS ----------------
def analyze_rotation(rot, allowances):

    countries = []
    layovers = 0

    for i in range(len(rot)):
        f = rot[i]

        country = AIRPORT_COUNTRY.get(f["arr"])
        if country:
            countries.append(country)

        # -------- LAYOVER LOGIC --------
        if i < len(rot) - 1:
            next_f = rot[i + 1]

            if f["arr"] != HOME_BASE:
                if detect_layover_type(f, next_f) == "LAYOVER_HOTEL":
                    layovers += 1

    unique_countries = list(set(countries))
    total_days = layovers + 1

    # -------- CAS LOGIC --------
    if rot[-1]["arr"] == HOME_BASE:
        indemnities = total_days - 0.5   # Cas A
        case = "Cas A (retour CDG -0.5)"
    else:
        indemnities = total_days         # Cas B
        case = "Cas B (night stop)"

    # -------- RATE --------
    rates = []

    for c in unique_countries:
        for key in allowances:
            if c.lower() in key.lower():
                rates.append(allowances[key])

    if not rates:
        rates = [177]

    avg_rate = sum(rates) / len(rates)
    total_eur = indemnities * avg_rate

    return {
        "Route": " → ".join([f"{f['dep']}-{f['arr']}" for f in rot]),
        "Pays": ", ".join(unique_countries),
        "Layovers hôtel": layovers,
        "Règle": case,
        "Indemnités": round(indemnities, 2),
        "Taux €": round(avg_rate, 2),
        "Total €": round(total_eur, 2)
    }


# ---------------- MAIN ----------------
if uploaded_file and allowance_file:

    allowances = load_allowances(allowance_file)
    flights = extract_flights(uploaded_file)
    rotations = build_rotations(flights)

    results = [analyze_rotation(r, allowances) for r in rotations]
    df = pd.DataFrame(results)

    st.subheader("📊 Résultat détaillé")
    st.dataframe(df, use_container_width=True)

    st.subheader("💰 Totaux")
    st.metric("Total indemnités", round(df["Indemnités"].sum(), 2))
    st.metric("Total €", f"{round(df['Total €'].sum(), 2)} €")

    st.download_button(
        "📥 Télécharger CSV",
        df.to_csv(index=False),
        "indemnites.csv"
    )

else:
    st.info("Upload ton planning AIMS + ton barème pour lancer le calcul.")
