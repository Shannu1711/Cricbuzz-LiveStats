import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)


def load_data(query):
    database_path = Path(__file__).parent / "data" / "cricbuzz.db"

    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(query, connection)


st.title("🏏 Cricbuzz LiveStats")
st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")

teams = load_data("SELECT team_name, country FROM teams")

players = load_data(
    "SELECT full_name, country, playing_role FROM players"
)

matches = load_data("""
    SELECT
        m.match_description AS "Match",
        m.match_format AS "Format",
        t1.team_name AS "Team 1",
        t2.team_name AS "Team 2",
        v.venue_name AS "Venue",
        m.status AS "Status",
        m.match_date AS "Date",
        winner.team_name AS "Winner",
        m.victory_margin AS "Victory Margin",
        m.victory_type AS "Margin Type"
    FROM matches AS m
    LEFT JOIN teams AS t1 ON m.team1_id = t1.team_id
    LEFT JOIN teams AS t2 ON m.team2_id = t2.team_id
    LEFT JOIN venues AS v ON m.venue_id = v.venue_id
    LEFT JOIN teams AS winner ON m.winner_team_id = winner.team_id
""")

format_summary = load_data("""
    SELECT
        match_format AS format,
        COUNT(*) AS total_matches
    FROM matches
    GROUP BY match_format
    ORDER BY total_matches DESC
""")

col1, col2, col3 = st.columns(3)
col1.metric("Teams", len(teams))
col2.metric("Players", len(players))
col3.metric("Matches", len(matches))

st.header("SQL Analytics: Matches by Format")

if not format_summary.empty:
    st.bar_chart(
        format_summary,
        x="format",
        y="total_matches",
    )
else:
    st.info("There are no matches to analyze yet.")

st.header("Matches")

if not matches.empty:
    formats = ["All"] + sorted(matches["Format"].dropna().unique().tolist())
    selected_format = st.selectbox("Filter by match format", formats)

    if selected_format == "All":
        displayed_matches = matches
    else:
        displayed_matches = matches[matches["Format"] == selected_format]

    st.dataframe(displayed_matches, use_container_width=True)
else:
    st.info("No matches are saved in the database yet.")

st.header("Teams")
st.dataframe(teams, use_container_width=True)

st.header("Players")
st.dataframe(players, use_container_width=True)