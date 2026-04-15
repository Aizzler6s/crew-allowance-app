import pdfplumber
import re
import pandas as pd


def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_flights_with_time(text):
    """
    Extract flights with:
    - departure
    - arrival
    - arrival time (Axx:xx)
    """

    pattern = re.findall(
        r"\b([A-Z]{3})\s+([A-Z]{3})\s+A(\d{2}:\d{2})",
        text
    )

    flights = []

    for dep, arr, time in pattern:
        flights.append({
            "dep": dep,
            "arr": arr,
            "time": time
        })

    return flights


def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


def group_into_days(flights):
    """
    Logic:
    - New day if:
        - gap > 8h
        - OR route break (dep != previous arrival)
    """

    if not flights:
        return []

    days = []
    current_day = [flights[0]]

    for i in range(1, len(flights)):
        prev = flights[i - 1]
        curr = flights[i]

        prev_time = time_to_minutes(prev["time"])
        curr_time = time_to_minutes(curr["time"])

        gap = curr_time - prev_time

        # Handle overnight
        if gap < 0:
            gap += 24 * 60

        if gap > 480 or curr["dep"] != prev["arr"]:
            days.append(current_day)
            current_day = [curr]
        else:
            current_day.append(curr)

    days.append(current_day)

    return days


def build_dataframe(days):
    data = []

    for i, day in enumerate(days, start=1):
        rotation = " → ".join([f"{f['dep']}-{f['arr']}" for f in day])
        last_dest = day[-1]["arr"]

        data.append({
            "day": i,
            "rotation": rotation,
            "last_dest": last_dest,
            "night_stop": 1 if last_dest != "CDG" else 0
        })

    return pd.DataFrame(data)
