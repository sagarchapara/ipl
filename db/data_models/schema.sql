-- Players Table
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    role VARCHAR(50),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    country VARCHAR(50),
    dob DATE,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Teams Table
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    gender VARCHAR(10),
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Stadiums Table
CREATE TABLE stadiums (
    stadium_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    country VARCHAR(50),
    capacity INTEGER,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Tournaments Table
CREATE TABLE tournaments (
    tournament_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    gender VARCHAR(10),
    format VARCHAR(20),
    season VARCHAR(50),
    host_country VARCHAR(50),
    outcome JSONB,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Matches Table
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    balls_per_over INTEGER,
    stadium_id INTEGER REFERENCES stadiums(stadium_id),
    tournament_id INTEGER REFERENCES tournaments(tournament_id),
    tournament_match_details JSONB,
    gender VARCHAR(10),
    match_dates DATE[],
    match_type VARCHAR(20),
    match_type_number INTEGER,
    season VARCHAR(50),
    team1_id INTEGER REFERENCES teams(team_id),
    team2_id INTEGER REFERENCES teams(team_id),
    outcome JSONB,
    toss JSONB,
    overs INTEGER,
    man_of_the_match INTEGER[],
    team_type VARCHAR(20),
    players JSONB,
    bowl_out JSONB,
    missing JSONB,
    officials JSONB,
    super_subs JSONB,
    total_stats JSONB,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Innings Table
CREATE TABLE innings (
    innings_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    batting_team_id INTEGER REFERENCES teams(team_id),
    bowling_team_id INTEGER REFERENCES teams(team_id),
    total_deliveries INTEGER,
    runs_scored INTEGER,
    wickets_lost INTEGER,
    overs_played FLOAT,
    extras JSONB,
    target JSONB,
    fall_of_wickets JSONB,
    absent_hurt JSONB,
    penalty_runs JSONB,
    declared BOOLEAN,
    forfeited BOOLEAN,
    powerplay JSONB,
    miscounted_overs JSONB,
    super_over BOOLEAN,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Balls Table
CREATE TABLE balls (
    ball_id SERIAL PRIMARY KEY,
    innings_id INTEGER REFERENCES innings(innings_id),
    match_id INTEGER REFERENCES matches(match_id),
    ball_number INTEGER,
    batsman_id INTEGER REFERENCES players(player_id),
    bowler_id INTEGER REFERENCES players(player_id),
    non_striker_id INTEGER REFERENCES players(player_id),
    runs JSONB,
    extras JSONB,
    wicket JSONB,
    replacement JSONB,
    review JSONB,
    is_powerplay BOOLEAN,
    powerplay_type VARCHAR(20)
);

-- PlayerStatsInnings Table
CREATE TABLE player_stats_innings (
    player_stats_innings_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    match_id INTEGER REFERENCES matches(match_id),
    innings_id INTEGER REFERENCES innings(innings_id),
    runs_scored INTEGER,
    balls_faced INTEGER,
    fours INTEGER,
    sixes INTEGER,
    strike_rate FLOAT,
    balls_bowled INTEGER,
    runs_conceded INTEGER,
    wickets_taken INTEGER,
    economy FLOAT,
    catches INTEGER,
    run_outs INTEGER,
    stumpings INTEGER,
    not_out BOOLEAN DEFAULT TRUE,
    did_not_bat BOOLEAN DEFAULT TRUE,
    did_not_bowl BOOLEAN DEFAULT TRUE,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- PlayerVsPlayerInnings Table
CREATE TABLE player_vs_player_innings (
    player_vs_player_innings_id SERIAL PRIMARY KEY,
    batsman_id INTEGER REFERENCES players(player_id),
    bowler_id INTEGER REFERENCES players(player_id),
    match_id INTEGER REFERENCES matches(match_id),
    innings_id INTEGER REFERENCES innings(innings_id),
    runs_scored INTEGER,
    balls_faced INTEGER,
    fours INTEGER,
    sixes INTEGER,
    strike_rate FLOAT,
    outs INTEGER,
    overs_bowled FLOAT,
    runs_conceded INTEGER,
    fours_conceded INTEGER,
    sixes_conceded INTEGER,
    wickets_taken INTEGER,
    economy FLOAT,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- PlayerStatsOver Table
CREATE TABLE player_stats_over (
    player_stats_over_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    match_id INTEGER REFERENCES matches(match_id),
    innings_id INTEGER REFERENCES innings(innings_id),
    over_number INTEGER,
    runs_scored INTEGER,
    balls_faced INTEGER,
    fours INTEGER,
    sixes INTEGER,
    strike_rate FLOAT,
    balls_bowled INTEGER,
    runs_conceded INTEGER,
    wickets_taken INTEGER,
    economy FLOAT,
    fours_conceded INTEGER,
    sixes_conceded INTEGER,
    not_out BOOLEAN DEFAULT TRUE,
    is_batting BOOLEAN DEFAULT FALSE,
    is_bowling BOOLEAN DEFAULT FALSE,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Partnerships Table
CREATE TABLE partnerships (
    partnership_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    innings_id INTEGER REFERENCES innings(innings_id),
    player1_id INTEGER REFERENCES players(player_id),
    player2_id INTEGER REFERENCES players(player_id),
    runs_scored INTEGER,
    balls_faced INTEGER,
    fours INTEGER,
    sixes INTEGER,
    out VARCHAR(20),
    strike_rate FLOAT,
    did_backfill BOOLEAN DEFAULT FALSE
);

-- Fielding Table
CREATE TABLE fielding (
    fielding_id SERIAL PRIMARY KEY,
    out_player_id INTEGER REFERENCES players(player_id),
    fielder_id INTEGER REFERENCES players(player_id),
    bowler_id INTEGER REFERENCES players(player_id),
    match_id INTEGER REFERENCES matches(match_id),
    innings_id INTEGER REFERENCES innings(innings_id),
    over_number INTEGER,
    ball_number INTEGER,
    out_type VARCHAR(20),
    did_backfill BOOLEAN DEFAULT FALSE
);










