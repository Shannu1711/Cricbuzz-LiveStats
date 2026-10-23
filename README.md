Cricbuzz LiveStats
An individual cricket analytics project by T. Shanmukha Pranay Goud, built with Python, Streamlit, SQLite, SQL, Pandas and Cricbuzz Cricket on RapidAPI. API responses use JSON over HTTP.
Project links
- Live dashboard: Open Cricbuzz LiveStats
- Live Matches page: View live matches
- GitHub source code: Shannu1711/Cricbuzz-LiveStats
The dashboard is deployed on Streamlit Community Cloud. Open the live dashboard to use the hosted application without installing Python.
Features
- Local database overview and SQL analytics charts.
- Manage Data and Manage Matches pages for database workflows.
- SQL Query Lab with 25 questions: 7 Easy, 13 Medium and 5 Hard.
- Match explorer with competition, format and team filters.
- Live Matches page that filters the provider feed for active match states.
- Most Runs leaderboard with a player table and top-ten runs chart. Default series ID: 9241 — Indian Premier League 2026.
The sidebar page called Recent Matches API currently uses the same /matches/v1/live feed as Live Matches. It can display completed records returned by that feed; it does not call a separate historical recent-match endpoint. Only the Most Runs player category is implemented in this version.
Requirements
Python 3.11 was used for development (Windows, Python 3.11.9). Dependencies are listed in requirements.txt: Streamlit, Pandas, Requests, python-dotenv, SQLAlchemy and Plotly. SQLite support is included with Python.

A RapidAPI account with access to Cricbuzz Cricket is required for the API pages. Access and request limits depend on the selected provider plan.
Windows setup
Open PowerShell in the project folder:
cd C:\projects\Cricbuzz-LiveStats
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
If the virtual environment already exists, reuse it. Create a file named .env in the project root, beside app.py:
RAPIDAPI_KEY=your_rapidapi_key_here
Use your own key. Keep .env private. The application uses this API host:
cricbuzz-cricket.p.rapidapi.com
Keep the supplied data/cricbuzz.db and sql/analytics_queries.sql in their folders. Start the application:
.\.venv\Scripts\python.exe -m streamlit run app.py
Open the local URL shown in the terminal. The port may vary. Stop the server with Ctrl+C.
Streamlit Community Cloud deployment
The deployment uses the GitHub repository Shannu1711/Cricbuzz-LiveStats, branch main, and main file app.py. Dependencies are installed from requirements.txt.

Configure the following root-level value privately in Advanced settings → Secrets (or the deployed app settings):
RAPIDAPI_KEY = "your_actual_rapidapi_key"
Replace the placeholder with your own key. Keep credentials out of GitHub and screenshots. The hosted API pages use the configured deployment credentials; visitors do not need to enter a key. Developers running their own copy must configure their own credentials.

The home page has been demonstrated on the hosted app. Check the API pages and SQL Query Lab after deployment. Treat SQLite changes on the hosted app as demonstration data; retain a separate backup of the supplied database.
Main files
Path	Purpose
app.py	Application entry point and database overview
services/cricbuzz_api.py	Requests and normalizes the match feed
pages/2_SQL_Analytics.py	Local analytics and charts
pages/3_Manage_Data.py	Data management interface
pages/4_Manage_Matches.py	Match management interface
pages/5_SQL_Query_Lab.py	Saved SQL questions and results
pages/6_Recent_Matches_API.py	Match explorer using the provider match feed
pages/7_Top_Player_Stats_API.py	Most Runs leaderboard request and display
pages/8_Live_Matches_API.py	Active-state match display
data/cricbuzz.db	SQLite database
sql/analytics_queries.sql	25 numbered analytics queries
database/	Database helpers and schema
requirements.txt	Python dependencies


The services folder belongs in the project root, beside pages.
API integration
Requests use HTTPS, a 20-second timeout, and the X-RapidAPI-Key and X-RapidAPI-Host headers.
Feature	Request
Match explorer and Live Matches	GET /matches/v1/live
Player Most Runs	GET /stats/v1/series/{series_id}?statsType=mostRuns


The match service flattens typeMatches → seriesMatches → seriesAdWrapper → matches, then reads match information and optional innings scores. Match pages cache responses for 60 seconds; use Refresh to request new data. Refresh is user initiated, so the page is not a continuously streaming score display.

The player page requests its leaderboard directly and builds a table from the returned headers and values. Enter a numeric series ID and click Load Player Stats. The default 9241 was verified with IPL 2026 results. Data availability varies by series and provider.

API results are displayed separately from SQLite. There is no automatic API-to-database synchronization. OpenCricket credentials are not used by the migrated pages.
Database and SQL practice
The database has seven related tables: teams, players, venues, series, matches, innings and player_innings_stats.

The checked database contains 3 teams, 7 players, 1 venue, 1 series, 1 match, 2 innings and 12 player innings records. These are demo/sample records, not a complete real-world cricket dataset. Player totals refer only to stored records, not full careers. Back up the database before changing or deleting records.

In SQL Query Lab, choose a difficulty and question, review the SQL, then click Run selected query. The lab opens SQLite in read-only mode and enables query_only; it displays saved SELECT and WITH queries.
Level	Questions	Topics
Easy	1–7	Teams, players, match joins, format/status counts, appearances and wins
Medium	8–20	Runs, boundaries, strike rates, wickets, economy and innings summaries
Hard	21–25	Window rankings, cumulative runs, venue comparisons, rolling win percentages and series ranks


All 25 revised queries executed successfully against the uploaded database. SQLite integrity_check returned ok, and foreign_key_check returned no violations. A small dataset does not verify every possible match scenario.
Troubleshooting
- Missing API key: check that .env is beside app.py, contains RAPIDAPI_KEY, and uses your current key. For the hosted app, check RAPIDAPI_KEY in Streamlit Secrets instead. Restart the app after configuration changes.
- Authentication, access or quota error: check the provider response and your RapidAPI credentials, API access and remaining quota.
- No live matches: the provider may return no active matches. The match explorer may still show completed records.
- No player results: confirm the series ID and try again when the provider has statistics available.
- Database or SQL file missing: restore the supplied files to the paths listed above. Do not create an empty replacement database or overwrite existing records unintentionally.
- Import error for services.cricbuzz_api: place the module in the root services folder and run Streamlit from the project root.
Demonstration and submission
Demonstrate the database overview, analytics charts, Query Lab, management pages, match explorer and Most Runs leaderboard. Explain the sample database and the shared match-feed endpoint. Show the no-active-match message if an active match is unavailable.

Include the application source, requirements, SQL schema and sample database, 25-query SQL file, README, project documentation and the recording if required by the instructor. Exclude the actual .env, virtual environment, Python cache folders and Git metadata from a submission archive. A placeholder .env.example may contain only RAPIDAPI_KEY=your_rapidapi_key_here.
Current verification and limitations
The app has been run locally and deployed on Streamlit Community Cloud, where the home page, database counts and chart have been demonstrated. API match records and the IPL Most Runs leaderboard were demonstrated during local development, and the SQL checks above passed. Final checks of the hosted API pages and Query Lab are still recommended. Management pages exist, but a complete final create/edit/delete regression pass is still recommended. A full automated test suite, completed recording and continuous active-score updates have not been confirmed.
