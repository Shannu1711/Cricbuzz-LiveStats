import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "cricbuzz.db"

st.set_page_config(
    page_title="Manage Matches | Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)


def read_data(query, params=()):
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection, params=params)


def write_data(query, params=()):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(query, params)


st.title("🏏 Manage Matches")
st.write("Create, view, edit, and delete match records.")


if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()


teams = read_data("""
    SELECT team_id, team_name
    FROM teams
    ORDER BY team_name
""")

if len(teams) < 2:
    st.warning("Add at least two teams in Manage Data before adding a match.")
    st.stop()


team_ids = teams["team_id"].astype(int).tolist()
team_names = {
    int(row["team_id"]): row["team_name"]
    for _, row in teams.iterrows()
}


def team_label(team_id):
    return f"{team_names[int(team_id)]} (ID {int(team_id)})"


def load_matches():
    return read_data("""
        SELECT
            m.match_id,
            m.match_description,
            m.match_format,
            m.team1_id,
            t1.team_name AS team1,
            m.team2_id,
            t2.team_name AS team2,
            m.match_date,
            m.status,
            m.winner_team_id,
            winner.team_name AS winner,
            m.victory_margin,
            m.victory_type
        FROM matches AS m
        LEFT JOIN teams AS t1 ON m.team1_id = t1.team_id
        LEFT JOIN teams AS t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams AS winner
            ON m.winner_team_id = winner.team_id
        ORDER BY m.match_date DESC
    """)


matches = load_matches()

st.subheader("Current matches")
st.dataframe(matches, hide_index=True, width="stretch")


# -------------------- CREATE MATCH --------------------
st.subheader("Add a match")

with st.form("add_match_form", clear_on_submit=True):
    description = st.text_input(
        "Match description",
        placeholder="Example: India vs Australia",
    )

    match_format = st.selectbox(
        "Match format",
        ["T20", "ODI", "Test"],
    )

    team1_id = st.selectbox(
        "Team 1",
        team_ids,
        format_func=team_label,
        key="create_team1",
    )

    team2_options = [team_id for team_id in team_ids if team_id != team1_id]

    team2_id = st.selectbox(
        "Team 2",
        team2_options,
        format_func=team_label,
        key="create_team2",
    )

    match_date = st.date_input("Match date", value=date.today())

    status = st.selectbox(
        "Status",
        ["Upcoming", "Live", "Completed"],
    )

    winner_options = [None] + team_ids
    winner_team_id = st.selectbox(
        "Winner (optional)",
        winner_options,
        format_func=lambda value: (
            "Not decided" if value is None else team_label(value)
        ),
        key="create_winner",
    )

    add_match = st.form_submit_button("Add match")


if add_match:
    if not description.strip():
        st.warning("Enter a match description.")
    elif team1_id == team2_id:
        st.warning("Choose two different teams.")
    else:
        try:
            write_data(
                """
                INSERT INTO matches
                    (match_description, match_format, team1_id, team2_id,
                     match_date, status, winner_team_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    description.strip(),
                    match_format,
                    int(team1_id),
                    int(team2_id),
                    match_date.isoformat(),
                    status,
                    (
                        int(winner_team_id)
                        if winner_team_id is not None
                        else None
                    ),
                ),
            )
            st.success("Match added.")
            st.rerun()
        except sqlite3.IntegrityError as error:
            st.error(f"Could not add the match: {error}")


# -------------------- EDIT OR DELETE MATCH --------------------
matches = load_matches()

if not matches.empty:
    st.subheader("Edit or delete a match")

    match_ids = matches["match_id"].astype(int).tolist()

    selected_match_id = st.selectbox(
        "Choose a match",
        match_ids,
        format_func=lambda match_id: (
            f"{matches.loc[matches['match_id'] == match_id, 'match_description'].iloc[0]}"
            f" (ID {match_id})"
        ),
        key="selected_match",
    )

    selected_match = matches[
        matches["match_id"] == selected_match_id
    ].iloc[0]

    current_team1_id = int(selected_match["team1_id"])
    current_team2_id = int(selected_match["team2_id"])

    all_formats = ["T20", "ODI", "Test"]
    if selected_match["match_format"] not in all_formats:
        all_formats.append(selected_match["match_format"])

    all_statuses = ["Upcoming", "Live", "Completed"]
    if selected_match["status"] not in all_statuses:
        all_statuses.append(selected_match["status"])

    try:
        current_date = date.fromisoformat(str(selected_match["match_date"]))
    except ValueError:
        current_date = date.today()

    with st.form("edit_match_form"):
        edited_description = st.text_input(
            "Match description",
            value=selected_match["match_description"],
        )

        edited_format = st.selectbox(
            "Match format",
            all_formats,
            index=all_formats.index(selected_match["match_format"]),
        )

        edited_team1_id = st.selectbox(
            "Team 1",
            team_ids,
            index=team_ids.index(current_team1_id),
            format_func=team_label,
            key="edit_team1",
        )

        edited_team2_options = [
            team_id for team_id in team_ids if team_id != edited_team1_id
        ]

        if current_team2_id not in edited_team2_options:
            current_team2_id = edited_team2_options[0]

        edited_team2_id = st.selectbox(
            "Team 2",
            edited_team2_options,
            index=edited_team2_options.index(current_team2_id),
            format_func=team_label,
            key="edit_team2",
        )

        edited_date = st.date_input(
            "Match date",
            value=current_date,
            key="edit_match_date",
        )

        edited_status = st.selectbox(
            "Status",
            all_statuses,
            index=all_statuses.index(selected_match["status"]),
        )

        current_winner = selected_match["winner_team_id"]
        if pd.isna(current_winner):
            current_winner = None
        else:
            current_winner = int(current_winner)

        winner_options = [None] + team_ids
        winner_index = winner_options.index(current_winner)

        edited_winner_id = st.selectbox(
            "Winner",
            winner_options,
            index=winner_index,
            format_func=lambda value: (
                "Not decided" if value is None else team_label(value)
            ),
            key="edit_winner",
        )

        confirm_delete = st.checkbox(
            "I confirm I want to delete this match"
        )

        save_match = st.form_submit_button("Save match changes")
        delete_match = st.form_submit_button("Delete match")

    if save_match:
        if not edited_description.strip():
            st.warning("Match description cannot be blank.")
        elif edited_team1_id == edited_team2_id:
            st.warning("Choose two different teams.")
        else:
            try:
                write_data(
                    """
                    UPDATE matches
                    SET match_description = ?,
                        match_format = ?,
                        team1_id = ?,
                        team2_id = ?,
                        match_date = ?,
                        status = ?,
                        winner_team_id = ?
                    WHERE match_id = ?
                    """,
                    (
                        edited_description.strip(),
                        edited_format,
                        int(edited_team1_id),
                        int(edited_team2_id),
                        edited_date.isoformat(),
                        edited_status,
                        (
                            int(edited_winner_id)
                            if edited_winner_id is not None
                            else None
                        ),
                        int(selected_match_id),
                    ),
                )
                st.success("Match updated.")
                st.rerun()
            except sqlite3.IntegrityError as error:
                st.error(f"Could not update the match: {error}")

    if delete_match:
        if not confirm_delete:
            st.warning("Tick the confirmation box before deleting.")
        else:
            try:
                write_data(
                    "DELETE FROM matches WHERE match_id = ?",
                    (int(selected_match_id),),
                )
                st.success("Match deleted.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error(
                    "This match has innings or player statistics linked to it, "
                    "so it cannot be deleted. You can still edit the match."
                )