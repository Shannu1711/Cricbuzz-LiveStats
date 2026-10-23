import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

API_HOST = "cricbuzz-cricket.p.rapidapi.com"
LIVE_URL = f"https://{API_HOST}/matches/v1/live"

# Load .env from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_live_matches():
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not api_key:
        raise RuntimeError("RAPIDAPI_KEY is missing from your project .env file.")

    response = requests.get(
        LIVE_URL,
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": API_HOST,
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    matches = []

    for match_group in payload.get("typeMatches", []):
        for series_group in match_group.get("seriesMatches", []):
            wrapper = series_group.get("seriesAdWrapper", {})

            for item in wrapper.get("matches", []):
                info = item.get("matchInfo", {})
                team1 = info.get("team1", {})
                team2 = info.get("team2", {})
                score = item.get("matchScore", {})

                teams = [
                    {"id": team1.get("teamId"), "name": team1.get("teamName", "Team 1")},
                    {"id": team2.get("teamId"), "name": team2.get("teamName", "Team 2")},
                ]
                team_names = {team["id"]: team["name"] for team in teams}

                innings = []
                for score_key, team_key in (
                    ("team1Score", "team1"),
                    ("team2Score", "team2"),
                ):
                    team_score = score.get(score_key, {})
                    team_id = info.get(team_key, {}).get("teamId")

                    for inning_key, inning in team_score.items():
                        if inning_key.startswith("inngs"):
                            innings.append({
                                "team_id": team_id,
                                "runs": inning.get("runs", 0),
                                "wickets": inning.get("wickets", 0),
                                "overs": inning.get("overs", "?"),
                            })

                start_date = info.get("startDate")
                if start_date:
                    try:
                        match_date = datetime.fromtimestamp(
                            int(start_date) / 1000
                        ).strftime("%d %b %Y, %I:%M %p")
                    except (TypeError, ValueError, OSError):
                        match_date = "Date unavailable"
                else:
                    match_date = "Date unavailable"

                venue = info.get("venueInfo", {})
                rows = {
                    "competition": {
                        "name": info.get("seriesName") or wrapper.get("seriesName", "Cricket")
                    },
                    "format": info.get("matchFormat", "Unknown"),
                    "teams": teams,
                    "team_names": team_names,
                    "innings": innings,
                    "date": match_date,
                    "result": info.get("status", ""),
                    "state": info.get("state", ""),
                    "match": info.get("matchDesc", "Match"),
                    "venue": venue.get("ground", ""),
                    "city": venue.get("city", ""),
                    "source": "Cricbuzz via RapidAPI",
                }
                matches.append(rows)

    return matches