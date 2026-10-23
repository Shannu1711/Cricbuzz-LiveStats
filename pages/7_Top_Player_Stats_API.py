import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


st.set_page_config(
    page_title="Top Player Stats",
    page_icon="🏏",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

API_HOST = "cricbuzz-cricket.p.rapidapi.com"

st.title("🏏 Top Player Stats")
st.caption("Series batting statistics from Cricbuzz via RapidAPI.")

series_id = st.text_input(
    "Cricbuzz Series ID",
    value="9241",
    help="9241 is IPL 2026. Enter another series ID to explore its statistics.",
)

st.caption("Category: Most Runs")


@st.cache_data(ttl=300)
def load_statistics(selected_series_id):
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "RAPIDAPI_KEY is missing from your project .env file."
        )

    response = requests.get(
        f"https://{API_HOST}/stats/v1/series/{selected_series_id}",
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": API_HOST,
        },
        params={"statsType": "mostRuns"},
        timeout=20,
    )

    response.raise_for_status()

    if not response.content.strip():
        raise RuntimeError(
            "The API returned an empty response. Check the series ID."
        )

    try:
        return response.json()
    except ValueError:
        raise RuntimeError(
            "The API returned an unexpected response. Please try again."
        ) from None


if st.button("Load Player Stats", type="primary"):
    # Clear the previous table before requesting another series.
    st.session_state.pop("rapidapi_player_stats", None)
    st.session_state.pop("rapidapi_stats_series_id", None)

    selected_id = series_id.strip()

    if not selected_id.isdigit():
        st.error("Enter a numeric Cricbuzz Series ID.")
    else:
        try:
            with st.spinner("Loading player statistics..."):
                payload = load_statistics(selected_id)

            st.session_state["rapidapi_player_stats"] = payload
            st.session_state["rapidapi_stats_series_id"] = selected_id

        except requests.exceptions.Timeout:
            st.error(
                "The API took too long to respond. Please try again."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Could not fetch statistics: {error}")

        except RuntimeError as error:
            st.error(str(error))


payload = st.session_state.get("rapidapi_player_stats")
loaded_id = st.session_state.get("rapidapi_stats_series_id")

if payload and loaded_id == series_id.strip():
    source_title = payload.get("appIndex", {}).get("seoTitle", "")

    st.subheader("Most Runs — IPL 2026" if loaded_id == "9241" else "Most Runs")

    if source_title:
        st.caption(source_title)

    tables_found = False

    for stats in payload.values():
        if not isinstance(stats, dict):
            continue

        headers = stats.get("headers")
        entries = stats.get("values")

        if not isinstance(headers, list) or not isinstance(entries, list):
            continue

        rows = [
            entry["values"]
            for entry in entries
            if isinstance(entry, dict)
            and isinstance(entry.get("values"), list)
        ]

        if not rows:
            continue

        columns = list(headers)

        # Cricbuzz includes a player ID before the displayed statistics.
        if len(rows[0]) == len(columns) + 1:
            columns = ["Player ID"] + columns

        if any(len(row) != len(columns) for row in rows):
            st.warning(
                "The API returned an unexpected statistics table format."
            )
            continue

        dataframe = pd.DataFrame(rows, columns=columns)
        tables_found = True

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

        if "Batter" in dataframe.columns and "R" in dataframe.columns:
            chart_data = dataframe[["Batter", "R"]].copy()

            chart_data["R"] = pd.to_numeric(
                chart_data["R"],
                errors="coerce",
            )

            chart_data = (
                chart_data.dropna(subset=["R"])
                .sort_values("R", ascending=False)
                .head(10)
            )

            if not chart_data.empty:
                st.subheader("Top 10 Batters by Runs")
                st.bar_chart(
                    chart_data.set_index("Batter"),
                    y="R",
                )

    if not tables_found:
        st.info(
            "No player statistics were returned for this series."
        )

    st.caption(
        f"Source: Cricbuzz via RapidAPI · Series ID: {loaded_id}"
    )