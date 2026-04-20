import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="NO GOAL 5 MIN SCANNER", layout="wide")

REFRESH_INTERVAL = 20

if "previous_data" not in st.session_state:
    st.session_state.previous_data = {}

# ---------------- MOCK DATA ----------------
def fetch_live_data():
    matches = []
    teams = [
        "Barcelona vs Sevilla",
        "Liverpool vs Chelsea",
        "Real Madrid vs Valencia",
        "Bayern vs Dortmund",
        "PSG vs Lyon",
    ]

    for i, match in enumerate(teams):
        minute = random.randint(10, 85)
        shots5 = random.randint(0, 3)
        shots10 = random.randint(0, 4)
        da = random.randint(10, 80)

        prev_da = st.session_state.previous_data.get(i, {}).get("da", da)

        matches.append({
            "id": i,
            "match": match,
            "minute": minute,
            "score": f"{random.randint(0,3)}-{random.randint(0,3)}",
            "shots5": shots5,
            "shots10": shots10,
            "da": da,
            "prev_da": prev_da,
            "corners5": random.randint(0, 3),
            "red": random.choice([0,0,0,1]),
            "recent_goal": random.choice([False, False, True]),
            "possession": random.randint(40, 60)
        })

    return matches

# ---------------- LOGIC ----------------
def calculate_signal(m):
    conditions = [
        m["shots5"] == 0,
        (m["da"] - m["prev_da"]) < 4,
        m["minute"] < 75,
        not m["recent_goal"],
        m["red"] == 0
    ]

    score = sum(conditions)

    if score == 5:
        return "STRONG"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "RISKY"

def safe_zone(m):
    return (
        (15 <= m["minute"] <= 40 or 55 <= m["minute"] <= 75)
        and (m["da"] / max(m["minute"],1)) < 1.2
        and m["shots10"] == 0
        and m["corners5"] == 0
    )

def confidence(m):
    if m["shots10"] == 0 and 40 <= m["possession"] <= 60:
        return "HIGH"
    elif m["shots5"] <= 1:
        return "MEDIUM"
    else:
        return "LOW"

# ---------------- UI ----------------
st.title("⚽ NO GOAL 5 MIN SCANNER")

c1, c2 = st.columns(2)
with c1:
    strong_only = st.checkbox("Show only STRONG")
with c2:
    safe_only = st.checkbox("Show SAFE only")

data = fetch_live_data()

rows = []

for m in data:
    delta = m["da"] - m["prev_da"]
    m["delta"] = delta

    signal = calculate_signal(m)
    safe = safe_zone(m)
    conf = confidence(m)

    st.session_state.previous_data[m["id"]] = {"da": m["da"]}

    if strong_only and signal != "STRONG":
        continue
    if safe_only and not safe:
        continue

    rows.append({
        "Match": m["match"],
        "Min": m["minute"],
        "Score": m["score"],
        "Shots(5m)": m["shots5"],
        "DA": m["da"],
        "ΔDA": delta,
        "Signal": signal,
        "Safe": "YES" if safe else "NO",
        "Confidence": conf
    })

df = pd.DataFrame(rows)

def color(val):
    if val == "STRONG":
        return "background-color: green; color:white"
    elif val == "MEDIUM":
        return "background-color: orange"
    else:
        return "background-color: red; color:white"

if not df.empty:
    st.dataframe(df.style.applymap(color, subset=["Signal"]), use_container_width=True)
else:
    st.warning("No matches found ⚠️")

st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

time.sleep(REFRESH_INTERVAL)
st.rerun()
