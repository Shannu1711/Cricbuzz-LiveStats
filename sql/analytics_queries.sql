-- Cricbuzz LiveStats: 25 SQL practice questions and answers
-- SQLite; validated against the supplied demonstration database.
-- All statistics describe only records stored in this database.
-- Dates must use a consistent sortable format for chronological queries.
-- Difficulty: 1-7 Easy, 8-20 Medium, 21-25 Hard.
-- This file contains SELECT queries only; it does not modify data.

-- 1. [Easy] List all teams
SELECT team_id, team_name, country FROM teams ORDER BY team_name;

-- 2. [Easy] List all players and roles
SELECT player_id, full_name, country, playing_role FROM players ORDER BY full_name;

-- 3. [Easy] Show matches with team names, venue and winner
SELECT m.match_id, m.match_description, m.match_format, t1.team_name AS team1, t2.team_name AS team2, v.venue_name, m.match_date, m.status, winner.team_name AS winner FROM matches m LEFT JOIN teams t1 ON m.team1_id=t1.team_id LEFT JOIN teams t2 ON m.team2_id=t2.team_id LEFT JOIN venues v ON m.venue_id=v.venue_id LEFT JOIN teams winner ON m.winner_team_id=winner.team_id ORDER BY m.match_date DESC;

-- 4. [Easy] Count matches by format
SELECT match_format, COUNT(*) AS match_count FROM matches GROUP BY match_format ORDER BY match_count DESC;

-- 5. [Easy] Count matches by status
SELECT status, COUNT(*) AS match_count FROM matches GROUP BY status ORDER BY match_count DESC;

-- 6. [Easy] Count match records involving each team
WITH team_appearances AS (SELECT team1_id AS team_id FROM matches UNION ALL SELECT team2_id FROM matches) SELECT t.team_name, COUNT(*) AS matches_played FROM team_appearances a JOIN teams t ON a.team_id=t.team_id GROUP BY t.team_id,t.team_name ORDER BY matches_played DESC;

-- 7. [Easy] Count wins by team
SELECT t.team_name, COUNT(m.match_id) AS wins FROM teams t LEFT JOIN matches m ON t.team_id=m.winner_team_id GROUP BY t.team_id,t.team_name ORDER BY wins DESC;

-- 8. [Medium] Rank players by runs in the stored dataset
SELECT p.full_name, SUM(ps.runs_scored) AS total_runs FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name ORDER BY total_runs DESC;

-- 9. [Medium] Calculate batting strike rates
SELECT p.full_name,SUM(ps.runs_scored) AS total_runs,SUM(ps.balls_faced) AS balls_faced,ROUND(100.0*SUM(ps.runs_scored)/NULLIF(SUM(ps.balls_faced),0),2) AS strike_rate FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name ORDER BY strike_rate DESC;

-- 10. [Medium] Find innings with at least 50 runs
SELECT p.full_name,m.match_description,ps.innings_number,ps.runs_scored,ps.balls_faced FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id JOIN matches m ON ps.match_id=m.match_id WHERE ps.runs_scored>=50 ORDER BY ps.runs_scored DESC;

-- 11. [Medium] Rank players by total boundaries
SELECT p.full_name,SUM(COALESCE(ps.fours,0)) AS total_fours,SUM(COALESCE(ps.sixes,0)) AS total_sixes,SUM(COALESCE(ps.fours,0)+COALESCE(ps.sixes,0)) AS total_boundaries FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name ORDER BY total_boundaries DESC;

-- 12. [Medium] Find the ten highest individual innings scores
SELECT p.full_name,m.match_description,ps.innings_number,ps.runs_scored FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id JOIN matches m ON ps.match_id=m.match_id ORDER BY ps.runs_scored DESC,ps.match_id,ps.player_id LIMIT 10;

-- 13. [Medium] Rank players by wickets
SELECT p.full_name,SUM(ps.wickets_taken) AS total_wickets FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name ORDER BY total_wickets DESC;

-- 14. [Medium] Calculate bowling economy rates
SELECT p.full_name,SUM(ps.runs_conceded) AS runs_conceded,SUM(ps.balls_bowled) AS balls_bowled,ROUND(6.0*SUM(ps.runs_conceded)/NULLIF(SUM(ps.balls_bowled),0),2) AS economy_rate FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name HAVING SUM(ps.balls_bowled)>0 ORDER BY economy_rate;

-- 15. [Medium] Calculate bowling strike rates
SELECT p.full_name,SUM(ps.wickets_taken) AS total_wickets,SUM(ps.balls_bowled) AS balls_bowled,ROUND(1.0*SUM(ps.balls_bowled)/NULLIF(SUM(ps.wickets_taken),0),2) AS bowling_strike_rate FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name HAVING SUM(ps.wickets_taken)>0 ORDER BY bowling_strike_rate;

-- 16. [Medium] Find innings with at least three wickets
SELECT p.full_name,m.match_description,ps.innings_number,ps.wickets_taken FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id JOIN matches m ON ps.match_id=m.match_id WHERE ps.wickets_taken>=3 ORDER BY ps.wickets_taken DESC;

-- 17. [Medium] Compare player runs and wickets
SELECT p.full_name,SUM(ps.runs_scored) AS total_runs,SUM(ps.wickets_taken) AS total_wickets FROM player_innings_stats ps JOIN players p ON ps.player_id=p.player_id GROUP BY p.player_id,p.full_name ORDER BY total_runs DESC,total_wickets DESC;

-- 18. [Medium] Calculate innings totals by batting team
SELECT t.team_name,SUM(i.total_runs) AS total_runs,SUM(i.wickets_lost) AS wickets_lost,COUNT(*) AS innings_played FROM innings i JOIN teams t ON i.batting_team_id=t.team_id GROUP BY t.team_id,t.team_name ORDER BY total_runs DESC;

-- 19. [Medium] Find each team highest innings score
SELECT t.team_name,MAX(i.total_runs) AS highest_innings_score FROM innings i JOIN teams t ON i.batting_team_id=t.team_id GROUP BY t.team_id,t.team_name ORDER BY highest_innings_score DESC;

-- 20. [Medium] Calculate average first-innings score by format
SELECT m.match_format,ROUND(AVG(i.total_runs),2) AS average_first_innings_score FROM innings i JOIN matches m ON i.match_id=m.match_id WHERE i.innings_number=1 GROUP BY m.match_format ORDER BY average_first_innings_score DESC;

-- 21. [Hard] Rank batters within each match format, keeping ties
WITH totals AS (
    SELECT m.match_format, p.player_id, p.full_name,
           SUM(COALESCE(ps.runs_scored, 0)) AS total_runs
    FROM player_innings_stats ps
    JOIN matches m ON m.match_id = ps.match_id
    JOIN players p ON p.player_id = ps.player_id
    WHERE COALESCE(ps.balls_faced, 0) > 0 OR COALESCE(ps.runs_scored, 0) > 0
    GROUP BY m.match_format, p.player_id, p.full_name
)
SELECT *, DENSE_RANK() OVER (
    PARTITION BY match_format ORDER BY total_runs DESC
) AS batting_rank
FROM totals
ORDER BY match_format, batting_rank, full_name;

-- 22. [Hard] Calculate each batter cumulative runs in chronological innings order
SELECT p.full_name, m.match_date, m.match_id, ps.innings_number,
       COALESCE(ps.runs_scored, 0) AS runs_scored,
       SUM(COALESCE(ps.runs_scored, 0)) OVER (
           PARTITION BY p.player_id
           ORDER BY m.match_date, m.match_id, ps.innings_number
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_runs
FROM player_innings_stats ps
JOIN players p ON p.player_id = ps.player_id
JOIN matches m ON m.match_id = ps.match_id
WHERE COALESCE(ps.balls_faced, 0) > 0 OR COALESCE(ps.runs_scored, 0) > 0
ORDER BY p.full_name, m.match_date, m.match_id, ps.innings_number;

-- 23. [Hard] Compare each innings score with the venue average for the same format
WITH scored AS (
    SELECT v.venue_name, m.match_format, m.match_id, i.innings_number,
           t.team_name, i.total_runs,
           AVG(i.total_runs) OVER (
               PARTITION BY v.venue_id, m.match_format
           ) AS venue_format_average
    FROM innings i
    JOIN matches m ON m.match_id = i.match_id
    JOIN venues v ON v.venue_id = m.venue_id
    JOIN teams t ON t.team_id = i.batting_team_id
)
SELECT *, ROUND(total_runs - venue_format_average, 2) AS runs_above_average
FROM scored
ORDER BY runs_above_average DESC, match_id, innings_number;

-- 24. [Hard] Calculate each team rolling win percentage over up to three completed matches with a winner
WITH appearances AS (
    SELECT match_id, match_date, team1_id AS team_id,
           CASE WHEN team1_id = winner_team_id THEN 1 ELSE 0 END AS won
    FROM matches WHERE LOWER(status) IN ('complete', 'completed')
      AND winner_team_id IS NOT NULL
    UNION ALL
    SELECT match_id, match_date, team2_id,
           CASE WHEN team2_id = winner_team_id THEN 1 ELSE 0 END
    FROM matches WHERE LOWER(status) IN ('complete', 'completed')
      AND winner_team_id IS NOT NULL
)
SELECT t.team_name, a.match_date, a.match_id, a.won,
       COUNT(*) OVER w AS matches_in_window,
       ROUND(100.0 * AVG(a.won) OVER w, 2) AS rolling_win_percentage
FROM appearances a JOIN teams t ON t.team_id = a.team_id
WINDOW w AS (
    PARTITION BY a.team_id ORDER BY a.match_date, a.match_id
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)
ORDER BY t.team_name, a.match_date, a.match_id;

-- 25. [Hard] Find the top three batting ranks per series, including ties
WITH totals AS (
    SELECT s.series_id, s.series_name, p.player_id, p.full_name,
           SUM(COALESCE(ps.runs_scored, 0)) AS total_runs
    FROM player_innings_stats ps
    JOIN matches m ON m.match_id = ps.match_id
    JOIN series s ON s.series_id = m.series_id
    JOIN players p ON p.player_id = ps.player_id
    WHERE COALESCE(ps.balls_faced, 0) > 0 OR COALESCE(ps.runs_scored, 0) > 0
    GROUP BY s.series_id, s.series_name, p.player_id, p.full_name
), ranked AS (
    SELECT *, DENSE_RANK() OVER (
        PARTITION BY series_id ORDER BY total_runs DESC
    ) AS batting_rank FROM totals
)
SELECT series_name, full_name, total_runs, batting_rank
FROM ranked WHERE batting_rank <= 3
ORDER BY series_name, batting_rank, full_name;
