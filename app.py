import streamlit as st
import pdfplumber
import pandas as pd

st.title("✈️ Crew Allowance (AIMS Horizontal FIXED)")

uploaded_file = st.file_uploader("Upload ton planning AIMS", type=["pdf"])

HOME_BASE = "CDG"


# ---------------- EXTRACTION PAR COORDONNÉES ----------------
def extract_columns(pdf_file):
    columns = {}

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:

            words = page.extract_words()

            for w in words:
                x = round(w["x0"] / 50)  # bucket horizontal (colonne approx)
                text = w["text"]

                if x not in columns:
                    columns[x] = []

                columns[x].append(text)

    # trier colonnes de gauche à droite
    sorted_cols = [columns[k] for k in sorted(columns.keys())]

    return sorted_cols


# ---------------- ANALYSE ----------------
def analyze_columns(cols):

    if not cols:
        return {"error": "no data"}

    last_col = cols[-1]

    # debug
    st.write("Dernière colonne détectée :", last_col)

    # détection CDG dans la dernière colonne
    has_cdg = any(HOME_BASE in str(cell) for cell in last_col)

    if has_cdg:
        nights = 0
        rule = "Cas A (retour CDG -0.5)"
    else:
        nights = 1
        rule = "Cas B (night stop)"

    return {
        "Night stop": nights,
        "Règle": rule,
        "CDG dans dernière colonne": has_cdg
    }


# ---------------- MAIN ----------------
if uploaded_file:

    cols = extract_columns(uploaded_file)

    result = analyze_columns(cols)

    st.subheader("🧠 Résultat")
    st.write(result)

    # DEBUG VISUEL
    st.subheader("🔎 Colonnes détectées")
    for i, col in enumerate(cols):
        st.write(f"Colonne {i+1}:", col)

else:
    st.info("Upload ton planning AIMS")
