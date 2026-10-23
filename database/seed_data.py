from db_connection import get_connection


def add_demo_data():
    with get_connection() as connection:
        # Add demo teams
        connection.executemany(
            """
            INSERT OR IGNORE INTO teams (team_id, team_name, country)
            VALUES (?, ?, ?)
            """,
            [
                (1, "Demo Team A", "Country A"),
                (2, "Demo Team B", "Country B"),
            ],
        )

        # Add six demo players
        connection.executemany(
            """
            INSERT OR IGNORE INTO players
                (player_id, full_name, country, playing_role)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "Demo Batter One", "Country A", "Batsman"),
                (2, "Demo Bowler One", "Country A", "Bowler"),
                (3, "Demo Batter Two", "Country B", "Batsman"),
                (4, "Demo Bowler Two", "Country B", "Bowler"),
                (5, "Demo All-rounder A", "Country A", "All-rounder"),
                (6, "Demo All-rounder B", "Country B", "All-rounder"),
            ],
        )

        # Add demo venue
        connection.execute(
            """
            INSERT OR IGNORE INTO venues
                (venue_id, venue_name, city, country, capacity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, "Demo Cricket Ground", "Demo City", "Country A", 30000),
        )

        # Add demo series
        connection.execute(
            """
            INSERT OR IGNORE INTO series
                (series_id, series_name, host_country, match_format,
                 start_date, planned_matches)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (1, "Demo Series", "Country A", "ODI", "2026-10-18", 3),
        )

        # Add demo match
        connection.execute(
            """
            INSERT OR IGNORE INTO matches
                (match_id, match_description, match_format, team1_id, team2_id,
                 venue_id, series_id, match_date, status, toss_winner_team_id,
                 toss_decision, winner_team_id, victory_margin, victory_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Demo Team A vs Demo Team B",
                "ODI",
                1,
                2,
                1,
                1,
                "2026-10-18",
                "Completed",
                1,
                "bat",
                1,
                20,
                "runs",
            ),
        )

        # Add the two innings
        connection.executemany(
            """
            INSERT OR IGNORE INTO innings
                (match_id, innings_number, batting_team_id, bowling_team_id,
                 total_runs, wickets_lost, overs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, 1, 1, 2, 250, 8, "50.0"),
                (1, 2, 2, 1, 230, 10, "48.3"),
            ],
        )

        # Add batting and bowling figures.
        # Each row is:
        # match_id, innings_number, player_id, batting_position,
        # runs_scored, balls_faced, fours, sixes,
        # balls_bowled, runs_conceded, wickets_taken, catches, stumpings
        connection.executemany(
            """
            INSERT OR IGNORE INTO player_innings_stats
                (match_id, innings_number, player_id, batting_position,
                 runs_scored, balls_faced, fours, sixes,
                 balls_bowled, runs_conceded, wickets_taken,
                 catches, stumpings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                # First innings: Demo Team A batting
                (1, 1, 1, 1, 85, 90, 9, 1, 0, 0, 0, 0, 0),
                (1, 1, 2, 2, 45, 50, 4, 1, 0, 0, 0, 0, 0),
                (1, 1, 5, 3, 110, 100, 10, 3, 0, 0, 0, 0, 0),

                # First innings: Demo Team B bowling
                (1, 1, 3, None, 0, 0, 0, 0, 120, 70, 2, 0, 0),
                (1, 1, 4, None, 0, 0, 0, 0, 90, 75, 3, 0, 0),
                (1, 1, 6, None, 0, 0, 0, 0, 90, 95, 3, 0, 0),

                # Second innings: Demo Team B batting
                (1, 2, 3, 1, 75, 80, 8, 1, 0, 0, 0, 0, 0),
                (1, 2, 4, 2, 25, 40, 2, 0, 0, 0, 0, 0, 0),
                (1, 2, 6, 3, 120, 100, 10, 3, 0, 0, 0, 0, 0),

                # Second innings: Demo Team A bowling
                (1, 2, 1, None, 0, 0, 0, 0, 120, 60, 3, 0, 0),
                (1, 2, 2, None, 0, 0, 0, 0, 90, 65, 2, 0, 0),
                (1, 2, 5, None, 0, 0, 0, 0, 81, 75, 3, 0, 0),
            ],
        )

    print("Demo teams, players, venue, series, match, innings, and player stats added.")


if __name__ == "__main__":
    add_demo_data()