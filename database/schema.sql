PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    country TEXT NOT NULL,
    playing_role TEXT,
    batting_style TEXT,
    bowling_style TEXT
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY,
    venue_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    capacity INTEGER
);

CREATE TABLE IF NOT EXISTS series (
    series_id INTEGER PRIMARY KEY,
    series_name TEXT NOT NULL,
    host_country TEXT NOT NULL,
    match_format TEXT NOT NULL,
    start_date TEXT,
    planned_matches INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    match_description TEXT NOT NULL,
    match_format TEXT NOT NULL,
    team1_id INTEGER NOT NULL,
    team2_id INTEGER NOT NULL,
    venue_id INTEGER,
    series_id INTEGER,
    match_date TEXT NOT NULL,
    status TEXT NOT NULL,
    toss_winner_team_id INTEGER,
    toss_decision TEXT,
    winner_team_id INTEGER,
    victory_margin INTEGER,
    victory_type TEXT,
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (toss_winner_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (winner_team_id) REFERENCES teams(team_id),
    CHECK (team1_id <> team2_id)
);

CREATE TABLE IF NOT EXISTS innings (
    match_id INTEGER NOT NULL,
    innings_number INTEGER NOT NULL,
    batting_team_id INTEGER NOT NULL,
    bowling_team_id INTEGER NOT NULL,
    total_runs INTEGER DEFAULT 0,
    wickets_lost INTEGER DEFAULT 0,
    overs TEXT,
    PRIMARY KEY (match_id, innings_number),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (batting_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (bowling_team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS player_innings_stats (
    match_id INTEGER NOT NULL,
    innings_number INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    batting_position INTEGER,
    runs_scored INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    balls_bowled INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    wickets_taken INTEGER DEFAULT 0,
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0,
    PRIMARY KEY (match_id, innings_number, player_id),
    FOREIGN KEY (match_id, innings_number)
        REFERENCES innings(match_id, innings_number),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_date
    ON matches(match_date);

CREATE INDEX IF NOT EXISTS idx_matches_format
    ON matches(match_format);

CREATE INDEX IF NOT EXISTS idx_player_stats_player
    ON player_innings_stats(player_id);

CREATE INDEX IF NOT EXISTS idx_player_stats_match
    ON player_innings_stats(match_id, innings_number);