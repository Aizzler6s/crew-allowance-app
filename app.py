import streamlit as st
import pandas as pd

st.title("✈️ Crew Allowance (XLS VERSION CLEAN)")

uploaded_file = st.file_uploader("Upload ton planning Excel", type=["xlsx", "xls"])

HOME_BASE = "CDG"


def analyze_excel(file):
    df = pd.read_excel(file, header=None)

    # afficher pour debug
    st.subheader("📊 Tableau brut")
    st.dataframe(df)

    # dernière colonne = dernier jour
    last_col = df.iloc[:, -1].astype(str)

    st.subheader("🔎 Dernier jour")
    st.write(last_col)

    # détection CDG
    has_cdg = last_col.str.contains(HOME_BASE).any()

    if has_cdg:
        nights = 0
        rule = "Cas A (retour CDG -0.5)"
    else:
        nights = 1
        rule = "Cas B (night stop)"

    return {
        "Night stop": nights,
        "Règle": rule
    }


if uploaded_file:
    result = analyze_excel(uploaded_file)

    st.subheader("🧠 Résultat")
    st.write(result)

else:
    st.info("Upload ton fichier Excel")
