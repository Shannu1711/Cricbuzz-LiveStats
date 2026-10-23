import streamlit as st
from services.cricbuzz_api import get_live_matches

st.set_page_config(page_title="Cricbuzz Live Matches", page_icon="🏏")
st.title("🏏 Cricbuzz Live Match Explorer")
st.caption("Live match data from Cricbuzz via RapidAPI.")

if st.button("Refresh matches"):
    st.cache_data.clear()


@st.cache_data(ttl=60)
def load_matches():
    return get_live_matches()


try:
    matches = load_matches()

    if not matches:
        st.info("No matches returned. There may be no live matches right now.")
    else:
        competitions = sorted({
            match["competition"]["name"] for match in matches
        })
        formats = sorted({match["format"] for match in matches})
        teams = sorted({
            team["name"]
            for match in matches
            for team in match["teams"]
        })

        col1, col2, col3 = st.columns(3)
        with col1:
            competition_filter = st.selectbox(
                "Competition", ["All"] + competitions
            )
        with col2:
            format_filter = st.selectbox("Format", ["All"] + formats)
        with col3:
            team_filter = st.selectbox("Team", ["All"] + teams)

        for match in matches:
            team_names = [team["name"] for team in match["teams"]]

            if competition_filter != "All" and match["competition"]["name"] != competition_filter:
                continue
            if format_filter != "All" and match["format"] != format_filter:
                continue
            if team_filter != "All" and team_filter not in team_names:
                continue

            st.divider()
            st.subheader(" vs ".join(team_names))
            st.caption(
                f"{match['competition']['name']} · {match['match']} · "
                f"{match['format']} · {match['date']}"
            )

            if match["venue"]:
                st.caption(f"📍 {match['venue']}, {match['city']}")

            if match["innings"]:
                columns = st.columns(len(match["innings"]))
                for column, inning in zip(columns, match["innings"]):
                    name = match["team_names"].get(inning["team_id"], "Team")
                    column.metric(
                        name,
                        f"{inning['runs']}/{inning['wickets']}",
                        f"{inning['overs']} overs",
                    )

            if match["result"]:
                st.write(f"**Status:** {match['result']}")
            st.caption(f"State: {match['state']} · {match['source']}")

except Exception as error:
    st.error(f"Could not load matches: {error}")
    st.caption("Check your RapidAPI subscription and local .env key.")