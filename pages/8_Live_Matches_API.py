import streamlit as st
from services.cricbuzz_api import get_live_matches

st.set_page_config(page_title="Live Cricket Matches", page_icon="🏏")
st.title("🏏 Live Cricket Matches")
st.caption("Live match data from Cricbuzz via RapidAPI.")

if st.button("Refresh Live Scores"):
    st.cache_data.clear()


@st.cache_data(ttl=60)
def load_matches():
    return get_live_matches()


try:
    matches = load_matches()

    active_matches = [
        match for match in matches
        if any(
            word in match.get("state", "").lower()
            for word in ("progress", "toss", "innings", "live")
        )
    ]

    if not active_matches:
        st.info("The RapidAPI connection works, but Cricbuzz returned no matches currently in progress.")
    else:
        st.success(f"{len(active_matches)} live match(es) found.")

        for match in active_matches:
            teams = match["teams"]
            st.divider()
            st.subheader(f"{teams[0]['name']} vs {teams[1]['name']}")
            st.caption(
                f"{match['competition']['name']} · {match['match']} · "
                f"{match['format']}"
            )

            if match["venue"]:
                st.caption(f"📍 {match['venue']}, {match['city']}")

            if match["innings"]:
                columns = st.columns(len(match["innings"]))
                for column, inning in zip(columns, match["innings"]):
                    team_name = match["team_names"].get(inning["team_id"], "Team")
                    column.metric(
                        team_name,
                        f"{inning['runs']}/{inning['wickets']}",
                        f"{inning['overs']} overs",
                    )

            st.write(f"**Status:** {match['result'] or match['state']}")
            st.caption(match["source"])

except Exception as error:
    st.error(f"Could not load live matches: {error}")
    st.caption("Check your RapidAPI subscription and the RAPIDAPI_KEY in your local .env file.")