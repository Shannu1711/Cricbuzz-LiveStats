import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Find data/cricbuzz.db relative to this file
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "cricbuzz.db"

st.set_page_config(
    page_title="SQL Analytics | Cricbuzz LiveStats",
    page_icon="📊",
    layout="wide",
)


def read_data(query, params=()):
    """Run a SELECT query against the SQLite database and return a DataFrame."""
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection, params=params)


st.title("📊 SQL Cricket Analytics")
st.write("Explore match, team, batting, and bowling statistics from the database.")

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.info("Check that your database file is inside the project's data folder.")
    st.stop()


# Load available filter choices
try:
    formats_df = read_data("""
        SELECT DISTINCT match_format
        FROM matches
        WHERE match_format IS NOT NULL
        ORDER BY match_format
    """)

    statuses_df = read_data("""
        SELECT DISTINCT status
        FROM matches
        WHERE status IS NOT NULL
        ORDER BY status
    """)

except Exception as error:
    st.error(f"Could not read the database: {error}")
    st.stop()


format_options = ["All formats"] + formats_df["match_format"].tolist()
status_options = ["All statuses"] + statuses_df["status"].tolist()


# Sidebar filters
st.sidebar.header("Filters")

selected_format = st.sidebar.selectbox(
    "Match format",
    format_options,
)

selected_status = st.sidebar.selectbox(
    "Match status",
    status_options,
)


# Build safe, parameterized SQL filters
conditions = []
query_params = []

if selected_format != "All formats":
    conditions.append("m.match_format = ?")
    query_params.append(selected_format)

if selected_status != "All statuses":
    conditions.append("m.status = ?")
    query_params.append(selected_status)

if conditions:
    filter_sql = "WHERE " + " AND ".join(conditions)
else:
    filter_sql = ""


# Matches with team and venue names
matches_query = f"""
    SELECT
        m.match_id,
        m.match_description,
        m.match_format,
        t1.team_name AS team1,
        t2.team_name AS team2,
        v.venue_name,
        v.city,
        m.match_date,
        m.status,
        winner.team_name AS winner,
        m.victory_margin,
        m.victory_type
    FROM matches AS m
    LEFT JOIN teams AS t1
        ON m.team1_id = t1.team_id
    LEFT JOIN teams AS t2
        ON m.team2_id = t2.team_id
    LEFT JOIN venues AS v
        ON m.venue_id = v.venue_id
    LEFT JOIN teams AS winner
        ON m.winner_team_id = winner.team_id
    {filter_sql}
    ORDER BY m.match_date DESC
"""

try:
    matches = read_data(matches_query, query_params)
except Exception as error:
    st.error(f"Could not load matches: {error}")
    st.stop()


# Summary cards
total_matches = len(matches)

if total_matches:
    completed_matches = int(matches["winner"].notna().sum())
    team_ids = pd.concat(
        [
            read_data(
                f"SELECT m.team1_id FROM matches AS m {filter_sql}",
                query_params,
            )["team1_id"],
            read_data(
                f"SELECT m.team2_id FROM matches AS m {filter_sql}",
                query_params,
            )["team2_id"],
        ],
        ignore_index=True,
    )
    teams_in_matches = int(team_ids.nunique())
else:
    completed_matches = 0
    teams_in_matches = 0

innings_count_df = read_data(f"""
    SELECT COUNT(*) AS innings_count
    FROM innings AS i
    JOIN matches AS m
        ON i.match_id = m.match_id
    {filter_sql}
""", query_params)

innings_count = int(innings_count_df.loc[0, "innings_count"])

card1, card2, card3, card4 = st.columns(4)
card1.metric("Matches", total_matches)
card2.metric("Matches with a winner", completed_matches)
card3.metric("Teams represented", teams_in_matches)
card4.metric("Innings recorded", innings_count)


# Matches by format chart
st.subheader("Matches by format")

matches_by_format = read_data(f"""
    SELECT
        m.match_format,
        COUNT(*) AS match_count
    FROM matches AS m
    {filter_sql}
    GROUP BY m.match_format
    ORDER BY match_count DESC
""", query_params)

if not matches_by_format.empty:
    format_chart = px.bar(
        matches_by_format,
        x="match_format",
        y="match_count",
        color="match_format",
        labels={
            "match_format": "Format",
            "match_count": "Number of matches",
        },
        title="Number of matches in each format",
    )
    st.plotly_chart(format_chart, width="stretch")
else:
    st.info("There are no matches for the selected filters yet.")


# Batting leaderboard
st.subheader("🏏 Top run scorers")

batting_query = f"""
    SELECT
        p.full_name AS player,
        SUM(ps.runs_scored) AS total_runs,
        SUM(ps.balls_faced) AS balls_faced,
        SUM(ps.fours) AS fours,
        SUM(ps.sixes) AS sixes,
        CASE
            WHEN SUM(ps.balls_faced) > 0
            THEN ROUND(
                100.0 * SUM(ps.runs_scored) / SUM(ps.balls_faced),
                2
            )
            ELSE 0
        END AS strike_rate
    FROM player_innings_stats AS ps
    JOIN players AS p
        ON ps.player_id = p.player_id
    JOIN matches AS m
        ON ps.match_id = m.match_id
    {filter_sql}
    GROUP BY p.player_id, p.full_name
    ORDER BY total_runs DESC
    LIMIT 10
"""

batting = read_data(batting_query, query_params)

if not batting.empty:
    batting_chart = px.bar(
        batting.sort_values("total_runs"),
        x="total_runs",
        y="player",
        orientation="h",
        hover_data=["balls_faced", "fours", "sixes", "strike_rate"],
        labels={
            "total_runs": "Runs",
            "player": "Player",
        },
        title="Top 10 players by total runs",
    )
    st.plotly_chart(batting_chart, width="stretch")
    st.dataframe(batting, hide_index=True, width="stretch")
else:
    st.info("No player batting statistics have been added yet.")


# Bowling leaderboard
st.subheader("🎯 Top wicket takers")

bowling_query = f"""
    SELECT
        p.full_name AS player,
        SUM(ps.wickets_taken) AS wickets,
        SUM(ps.runs_conceded) AS runs_conceded,
        SUM(ps.balls_bowled) AS balls_bowled,
        CASE
            WHEN SUM(ps.balls_bowled) > 0
            THEN ROUND(
                6.0 * SUM(ps.runs_conceded) / SUM(ps.balls_bowled),
                2
            )
            ELSE 0
        END AS economy
    FROM player_innings_stats AS ps
    JOIN players AS p
        ON ps.player_id = p.player_id
    JOIN matches AS m
        ON ps.match_id = m.match_id
    {filter_sql}
    GROUP BY p.player_id, p.full_name
    HAVING SUM(ps.wickets_taken) > 0
    ORDER BY wickets DESC, economy ASC
    LIMIT 10
"""

bowling = read_data(bowling_query, query_params)

if not bowling.empty:
    bowling_chart = px.bar(
        bowling.sort_values("wickets"),
        x="wickets",
        y="player",
        orientation="h",
        hover_data=["runs_conceded", "balls_bowled", "economy"],
        labels={
            "wickets": "Wickets",
            "player": "Player",
        },
        title="Top 10 players by wickets",
    )
    st.plotly_chart(bowling_chart, width="stretch")
    st.dataframe(bowling, hide_index=True, width="stretch")
else:
    st.info("No player bowling statistics have been added yet.")


# Runs scored by batting team
st.subheader("🏆 Runs by batting team")

team_runs_query = f"""
    SELECT
        t.team_name,
        SUM(i.total_runs) AS total_runs,
        SUM(i.wickets_lost) AS wickets_lost,
        COUNT(*) AS innings_played
    FROM innings AS i
    JOIN teams AS t
        ON i.batting_team_id = t.team_id
    JOIN matches AS m
        ON i.match_id = m.match_id
    {filter_sql}
    GROUP BY t.team_id, t.team_name
    ORDER BY total_runs DESC
"""

team_runs = read_data(team_runs_query, query_params)

if not team_runs.empty:
    team_chart = px.bar(
        team_runs,
        x="team_name",
        y="total_runs",
        color="team_name",
        hover_data=["wickets_lost", "innings_played"],
        labels={
            "team_name": "Team",
            "total_runs": "Runs",
        },
        title="Total innings runs by team",
    )
    st.plotly_chart(team_chart, width="stretch")
    st.dataframe(team_runs, hide_index=True, width="stretch")
else:
    st.info("No innings data has been added yet.")


# Match results table
st.subheader("📋 Match results")

if not matches.empty:
    st.dataframe(matches, hide_index=True, width="stretch")
else:
    st.info("No matches match these filters.")