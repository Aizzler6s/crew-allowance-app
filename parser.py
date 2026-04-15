import pdfplumber
import re
import pandas as pd


def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def parse_flights(text):
    """
    Extract flights like:
    CDG -> KRK
    KRK -> CDG
    """
    pattern = re.findall(r"\b([A-Z]{3})\s+([A-Z]{3})\b", text)

    flights = []
    for dep, arr in pattern:
        flights.append((dep, arr))

    return flights


def group_by_day(text, flights):
    """
    Split roughly by days using dates (01/03 etc.)
    """
    days = re.split(r"\d{2}/\d{2}", text)

    results = []

    flight_index = 0

    for i, day_text in enumerate(days[1:], start=1):
        day_flights = []

        # heuristic: take next flights until next block
        for _ in range(6):  # max flights/day (safe)
            if flight_index < len(flights):
                dep, arr = flights[flight_index]
                day_flights.append(f"{dep}-{arr}")
                flight_index += 1

        if day_flights:
            results.append({
                "day": i,
                "rotation": " → ".join(day_flights),
                "last_dest": day_flights[-1].split("-")[1]
            })

    return results


def compute_night_stops(days_data):
    for day in days_data:
        if day["last_dest"] != "CDG":
            day["night_stop"] = 1
        else:
            day["night_stop"] = 0

    return days_data


def build_dataframe(days_data):
    df = pd.DataFrame(days_data)
    return df
