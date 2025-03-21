-- Raw rows for recent `n` logic
CREATE INDEX idx_stats_innings_player_match ON player_stats_innings(player_id, match_id DESC);
CREATE INDEX idx_pvp_innings_batsman_bowler_match ON player_vs_player_innings(batsman_id, bowler_id, match_id DESC);

-- For joins/filters
CREATE INDEX idx_matches_tournament_id ON matches(tournament_id);
CREATE INDEX idx_matches_stadium_id ON matches(stadium_id);
CREATE INDEX idx_matches_team1_team2 ON matches(team1_id, team2_id);

CREATE MATERIALIZED VIEW player_vs_player_totals_mv AS
SELECT
    batsman_id,
    bowler_id,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(outs) AS total_outs,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(overs_bowled) AS total_overs_bowled,
    SUM(wickets_taken) AS total_wickets_taken
FROM player_vs_player_innings
GROUP BY batsman_id, bowler_id;


CREATE MATERIALIZED VIEW player_vs_over_totals_mv AS
SELECT
    player_id,
    over_number,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(balls_bowled) AS total_balls_bowled,
    SUM(wickets_taken) AS total_wickets_taken,
    SUM(fours_conceded) AS total_fours_conceded,
    SUM(sixes_conceded) AS total_sixes_conceded,
    COUNT(*) FILTER (WHERE is_batting) AS innings_batted,
    COUNT(*) FILTER (WHERE is_bowling) AS innings_bowled
FROM player_stats_over
GROUP BY player_id, over_number;


CREATE MATERIALIZED VIEW player_totals_mv AS
SELECT
    player_id,
    COUNT(DISTINCT match_id) AS total_matches,
    COUNT(*) FILTER (WHERE did_not_bat = FALSE) AS total_innings_batted,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(CASE WHEN not_out THEN 1 ELSE 0 END) AS total_not_outs,
    COUNT(*) FILTER (WHERE did_not_bowl = FALSE) AS total_innings_bowled,
    SUM(balls_bowled) AS total_balls_bowled,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(wickets_taken) AS total_wickets_taken,
    SUM(catches) AS total_catches,
    SUM(run_outs) AS total_run_outs,
    SUM(stumpings) AS total_stumpings
FROM player_stats_innings
GROUP BY player_id;

CREATE MATERIALIZED VIEW partnership_totals_mv AS
SELECT
    LEAST(player1_id, player2_id) AS player1_id,
    GREATEST(player1_id, player2_id) AS player2_id,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    COUNT(*) AS total_partnerships,
    COUNT(*) FILTER (WHERE out IS NULL OR out = '') AS total_unbeaten_partnerships,
    MAX(match_id) AS last_match_id
FROM partnerships
GROUP BY LEAST(player1_id, player2_id), GREATEST(player1_id, player2_id);

CREATE MATERIALIZED VIEW player_totals_by_tournament_mv AS
SELECT
    player_id,
    m.tournament_id,
    COUNT(DISTINCT psi.match_id) AS total_matches,
    COUNT(*) FILTER (WHERE did_not_bat = FALSE) AS total_innings_batted,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(CASE WHEN not_out THEN 1 ELSE 0 END) AS total_not_outs,
    COUNT(*) FILTER (WHERE did_not_bowl = FALSE) AS total_innings_bowled,
    SUM(balls_bowled) AS total_balls_bowled,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(wickets_taken) AS total_wickets_taken,
    SUM(catches) AS total_catches,
    SUM(run_outs) AS total_run_outs,
    SUM(stumpings) AS total_stumpings
FROM player_stats_innings psi
JOIN matches m ON psi.match_id = m.match_id
GROUP BY player_id, m.tournament_id;

CREATE MATERIALIZED VIEW player_totals_by_stadium_mv AS
SELECT
    player_id,
    m.stadium_id,
    COUNT(DISTINCT psi.match_id) AS total_matches,
    COUNT(*) FILTER (WHERE did_not_bat = FALSE) AS total_innings_batted,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(CASE WHEN not_out THEN 1 ELSE 0 END) AS total_not_outs,
    COUNT(*) FILTER (WHERE did_not_bowl = FALSE) AS total_innings_bowled,
    SUM(balls_bowled) AS total_balls_bowled,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(wickets_taken) AS total_wickets_taken,
    SUM(catches) AS total_catches,
    SUM(run_outs) AS total_run_outs,
    SUM(stumpings) AS total_stumpings
FROM player_stats_innings psi
JOIN matches m ON psi.match_id = m.match_id
GROUP BY player_id, m.stadium_id;

CREATE MATERIALIZED VIEW player_totals_by_opposition_mv AS
SELECT
    psi.player_id,
    CASE
        WHEN m.team1_id = psi_team.team_id THEN m.team2_id
        ELSE m.team1_id
    END AS opposition_team_id,
    COUNT(DISTINCT psi.match_id) AS total_matches,
    COUNT(*) FILTER (WHERE did_not_bat = FALSE) AS total_innings_batted,
    SUM(runs_scored) AS total_runs_scored,
    SUM(balls_faced) AS total_balls_faced,
    SUM(fours) AS total_fours,
    SUM(sixes) AS total_sixes,
    SUM(CASE WHEN not_out THEN 1 ELSE 0 END) AS total_not_outs,
    COUNT(*) FILTER (WHERE did_not_bowl = FALSE) AS total_innings_bowled,
    SUM(balls_bowled) AS total_balls_bowled,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(wickets_taken) AS total_wickets_taken,
    SUM(catches) AS total_catches,
    SUM(run_outs) AS total_run_outs,
    SUM(stumpings) AS total_stumpings
FROM player_stats_innings psi
JOIN matches m ON psi.match_id = m.match_id
JOIN teams psi_team ON psi_team.team_id = (
    CASE
        WHEN m.team1_id = psi.player_id THEN m.team1_id
        ELSE m.team2_id
    END
)
GROUP BY psi.player_id, opposition_team_id;

-- Lifetime aggregates
CREATE INDEX idx_player_totals_mv_player ON player_totals_mv(player_id);
CREATE INDEX idx_pvp_totals_batsman_bowler ON player_vs_player_totals_mv(batsman_id, bowler_id);




