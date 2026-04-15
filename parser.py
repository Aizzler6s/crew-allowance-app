import pdfplumber
import re
import pandas as pd


def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_flights_with_time(text):
    """
    Extract flights with departure, arrival + time
    Example:
    CDG KRK A06:27 → CDG → KRK at 06:27
    """

    pattern = re.findall(
        r"([A-Z]{3})\s+([A-Z]{3}).*?A(\d{2}:\d{2})",
        text,
        re.DOTALL
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
    New logic:
    - if gap between flights > 8h → new day
    - if dep != previous arrival → new duty/day
    """

    days = []
    current_day = []

    for i, flight in enumerate(flights):

        if i == 0:
            current_day.append(flight)
            continue

        prev = flights[i - 1]

        time_gap = time_to_minutes(flight["time"]) - time_to_minutes(prev["time"])

        # handle midnight wrap
        if time_gap < 0:
            time_gap += 24 * 60

        # RULES 👇
        if time_gap > 480 or flight["dep"] != prev["arr"]:
            days.append(current_day)
            current_day = [flight]
        else:
            current_day.append(flight)

    if current_day:
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
