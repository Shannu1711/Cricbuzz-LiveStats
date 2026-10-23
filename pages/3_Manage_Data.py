import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "cricbuzz.db"

st.set_page_config(
    page_title="Manage Data | Cricbuzz LiveStats",
    page_icon="🛠️",
    layout="wide",
)


def read_data(query, params=()):
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection, params=params)


def write_data(query, params=()):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(query, params)


def show_error(error):
    st.error(f"Could not complete that action: {error}")


st.title("🛠️ Manage Cricket Data")
st.write("Add, view, edit, or delete teams and players in your database.")

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()


teams_tab, players_tab = st.tabs(["Teams", "Players"])


# -------------------- TEAMS --------------------
with teams_tab:
    st.header("Manage teams")

    teams = read_data("""
        SELECT team_id, team_name, country
        FROM teams
        ORDER BY team_name
    """)

    st.subheader("Current teams")
    st.dataframe(teams, hide_index=True, width="stretch")

    st.subheader("Add a team")
    with st.form("add_team_form", clear_on_submit=True):
        new_team_name = st.text_input("Team name")
        new_team_country = st.text_input("Country")
        add_team = st.form_submit_button("Add team")

    if add_team:
        if not new_team_name.strip() or not new_team_country.strip():
            st.warning("Enter both a team name and country.")
        else:
            try:
                write_data(
                    """
                    INSERT INTO teams (team_name, country)
                    VALUES (?, ?)
                    """,
                    (new_team_name.strip(), new_team_country.strip()),
                )
                st.success("Team added.")
                st.rerun()
            except sqlite3.IntegrityError as error:
                show_error(error)

    teams = read_data("""
        SELECT team_id, team_name, country
        FROM teams
        ORDER BY team_name
    """)

    if not teams.empty:
        st.subheader("Edit or delete a team")

        team_ids = teams["team_id"].astype(int).tolist()
        team_names = {
            int(row["team_id"]): row["team_name"]
            for _, row in teams.iterrows()
        }

        selected_team_id = st.selectbox(
            "Choose a team",
            team_ids,
            format_func=lambda team_id: (
                f"{team_names[team_id]} (ID {team_id})"
            ),
            key="selected_team",
        )

        selected_team = teams[
            teams["team_id"] == selected_team_id
        ].iloc[0]

        with st.form("edit_team_form"):
            edited_team_name = st.text_input(
                "Team name",
                value=selected_team["team_name"],
            )
            edited_team_country = st.text_input(
                "Country",
                value=selected_team["country"],
            )
            confirm_team_delete = st.checkbox(
                "I confirm I want to delete this team"
            )

            save_team = st.form_submit_button("Save team changes")
            delete_team = st.form_submit_button("Delete team")

        if save_team:
            if not edited_team_name.strip() or not edited_team_country.strip():
                st.warning("Team name and country cannot be blank.")
            else:
                try:
                    write_data(
                        """
                        UPDATE teams
                        SET team_name = ?, country = ?
                        WHERE team_id = ?
                        """,
                        (
                            edited_team_name.strip(),
                            edited_team_country.strip(),
                            int(selected_team_id),
                        ),
                    )
                    st.success("Team updated.")
                    st.rerun()
                except sqlite3.IntegrityError as error:
                    show_error(error)

        if delete_team:
            if not confirm_team_delete:
                st.warning("Tick the confirmation box before deleting.")
            else:
                try:
                    write_data(
                        "DELETE FROM teams WHERE team_id = ?",
                        (int(selected_team_id),),
                    )
                    st.success("Team deleted.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(
                        "This team is linked to a match or innings, so it "
                        "cannot be deleted. You can still edit the team."
                    )


# -------------------- PLAYERS --------------------
with players_tab:
    st.header("Manage players")

    players = read_data("""
        SELECT
            player_id,
            full_name,
            country,
            playing_role,
            batting_style,
            bowling_style
        FROM players
        ORDER BY full_name
    """)

    st.subheader("Current players")
    st.dataframe(players, hide_index=True, width="stretch")

    st.subheader("Add a player")
    with st.form("add_player_form", clear_on_submit=True):
        new_player_name = st.text_input("Full name")
        new_player_country = st.text_input("Player's country")
        new_player_role = st.text_input("Playing role (for example: Batter)")
        new_batting_style = st.text_input("Batting style (optional)")
        new_bowling_style = st.text_input("Bowling style (optional)")
        add_player = st.form_submit_button("Add player")

    if add_player:
        if not new_player_name.strip() or not new_player_country.strip():
            st.warning("Enter the player's name and country.")
        else:
            try:
                write_data(
                    """
                    INSERT INTO players
                        (full_name, country, playing_role,
                         batting_style, bowling_style)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        new_player_name.strip(),
                        new_player_country.strip(),
                        new_player_role.strip() or None,
                        new_batting_style.strip() or None,
                        new_bowling_style.strip() or None,
                    ),
                )
                st.success("Player added.")
                st.rerun()
            except sqlite3.IntegrityError as error:
                show_error(error)

    players = read_data("""
        SELECT
            player_id,
            full_name,
            country,
            playing_role,
            batting_style,
            bowling_style
        FROM players
        ORDER BY full_name
    """)

    if not players.empty:
        st.subheader("Edit or delete a player")

        player_ids = players["player_id"].astype(int).tolist()
        player_names = {
            int(row["player_id"]): row["full_name"]
            for _, row in players.iterrows()
        }

        selected_player_id = st.selectbox(
            "Choose a player",
            player_ids,
            format_func=lambda player_id: (
                f"{player_names[player_id]} (ID {player_id})"
            ),
            key="selected_player",
        )

        selected_player = players[
            players["player_id"] == selected_player_id
        ].iloc[0]

        with st.form("edit_player_form"):
            edited_player_name = st.text_input(
                "Full name",
                value=selected_player["full_name"],
            )
            edited_player_country = st.text_input(
                "Country",
                value=selected_player["country"],
            )
            edited_player_role = st.text_input(
                "Playing role",
                value=selected_player["playing_role"] or "",
            )
            edited_batting_style = st.text_input(
                "Batting style",
                value=selected_player["batting_style"] or "",
            )
            edited_bowling_style = st.text_input(
                "Bowling style",
                value=selected_player["bowling_style"] or "",
            )
            confirm_player_delete = st.checkbox(
                "I confirm I want to delete this player"
            )

            save_player = st.form_submit_button("Save player changes")
            delete_player = st.form_submit_button("Delete player")

        if save_player:
            if not edited_player_name.strip() or not edited_player_country.strip():
                st.warning("Player name and country cannot be blank.")
            else:
                try:
                    write_data(
                        """
                        UPDATE players
                        SET full_name = ?,
                            country = ?,
                            playing_role = ?,
                            batting_style = ?,
                            bowling_style = ?
                        WHERE player_id = ?
                        """,
                        (
                            edited_player_name.strip(),
                            edited_player_country.strip(),
                            edited_player_role.strip() or None,
                            edited_batting_style.strip() or None,
                            edited_bowling_style.strip() or None,
                            int(selected_player_id),
                        ),
                    )
                    st.success("Player updated.")
                    st.rerun()
                except sqlite3.IntegrityError as error:
                    show_error(error)

        if delete_player:
            if not confirm_player_delete:
                st.warning("Tick the confirmation box before deleting.")
            else:
                try:
                    write_data(
                        "DELETE FROM players WHERE player_id = ?",
                        (int(selected_player_id),),
                    )
                    st.success("Player deleted.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(
                        "This player is linked to match statistics, so they "
                        "cannot be deleted. You can still edit the player."
                    )