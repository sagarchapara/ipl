from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

Base = declarative_base()

# Players Table
class Player(Base):
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    role = Column(String(50))
    batting_style = Column(String(50))
    bowling_style = Column(String(50))
    country = Column(String(50))
    dob = Column(Date)

# Teams Table
class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    country = Column(String(50), nullable=False) #need to fill this later
    gender = Column(String(10))

# Stadiums Table
class Stadium(Base):
    __tablename__ = 'stadiums'
    stadium_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50))
    country = Column(String(50)) #need to fill this later
    capacity = Column(Integer) #need to fill this later

# Tournaments Table
class Tournament(Base):
    __tablename__ = 'tournaments'
    tournament_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    gender = Column(String(10))
    format = Column(String(20))
    season = Column(String(50))
    host_country = Column(String(50)) #need to fill this later
    outcome = Column(JSONB) #need to fill this later

# Matches Table
class Match(Base):
    __tablename__ = 'matches'
    match_id = Column(Integer, primary_key=True)

    balls_per_over = Column(Integer)

    stadium_id = Column(Integer, ForeignKey('stadiums.stadium_id'))
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    tournament_match_details = Column(JSONB)

    gender = Column(String(10))

    match_dates = Column(ARRAY(Date), nullable=False)
    match_type = Column(String(20))
    match_type_number = Column(Integer)
    season = Column(String(50))

    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    outcome = Column(JSONB)
    toss = Column(JSONB)

    overs = Column(Integer)
    man_of_the_match = Column(ARRAY(Integer))
    team_type = Column(String(20)) #International, Domestic, Club, Other

    players = Column(JSONB)

    bowl_out = Column(JSONB)
    missing = Column(JSONB)
    officials = Column(JSONB)
    super_subs = Column(JSONB)



# Innings Table
class Innings(Base):
    __tablename__ = 'innings'
    innings_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    batting_team_id = Column(Integer, ForeignKey('teams.team_id'))
    bowling_team_id = Column(Integer, ForeignKey('teams.team_id'))
    total_deliveries = Column(Integer)
    runs_scored = Column(Integer)
    wickets_lost = Column(Integer)
    overs_played = Column(Float)
    extras = Column(JSONB)
    target = Column(JSONB)
    fall_of_wickets = Column(JSONB)
    absent_hurt = Column(JSONB)
    penalty_runs = Column(JSONB)
    declared = Column(Boolean)
    forfeited = Column(Boolean)
    powerplay = Column(JSONB)
    miscounted_overs = Column(JSONB)
    target = Column(JSONB)
    super_over = Column(Boolean)
 
# Balls Table
class Ball(Base):
    __tablename__ = 'balls'
    ball_id = Column(Integer, primary_key=True)
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    ball_number = Column(Integer)
    batsman_id = Column(Integer, ForeignKey('players.player_id'))
    bowler_id = Column(Integer, ForeignKey('players.player_id'))
    non_striker_id = Column(Integer, ForeignKey('players.player_id'))
    runs = Column(JSONB)
    extras = Column(JSONB)
    wicket = Column(JSONB)
    replacement = Column(JSONB)
    review = Column(JSONB)
    is_powerplay = Column(Boolean)
    powerplay_type = Column(String(20))

# PlayerStatsInnings Table
class PlayerStatsInnings(Base):
    __tablename__ = 'player_stats_innings'
    player_stats_innings_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    runs_scored = Column(Integer)
    balls_faced = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    strike_rate = Column(Float)
    balls_bowled = Column(Integer)
    runs_conceded = Column(Integer)
    wickets_taken = Column(Integer)
    economy = Column(Float)
    catches = Column(Integer)
    run_outs = Column(Integer)
    stumpings = Column(Integer)
    not_out = Column(Boolean, default=True)
    did_not_bat = Column(Boolean, default=True)
    did_not_bowl = Column(Boolean, default=True)

# PlayerVsPlayerInnings Table
class PlayerVsPlayerInnings(Base):
    __tablename__ = 'player_vs_player_innings'
    player_vs_player_innings_id = Column(Integer, primary_key=True)
    batsman_id = Column(Integer, ForeignKey('players.player_id')) # in case of fielding, this will be the fielder, when the other player is out
    bowler_id = Column(Integer, ForeignKey('players.player_id'))
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    runs_scored = Column(Integer)
    balls_faced = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    strike_rate = Column(Float)
    outs = Column(Integer)
    overs_bowled = Column(Float)
    runs_conceded = Column(Integer)
    fours_conceded = Column(Integer)
    sixes_conceded = Column(Integer)
    wickets_taken = Column(Integer)
    economy = Column(Float)

class PlayerStatsOver(Base):
    __tablename__ = 'player_stats_over'
    player_stats_over_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    over_number = Column(Integer)
    runs_scored = Column(Integer)
    balls_faced = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    strike_rate = Column(Float)
    balls_bowled = Column(Integer)
    runs_conceded = Column(Integer)
    wickets_taken = Column(Integer)
    economy = Column(Float)
    fours_conceded = Column(Integer)
    sixes_conceded = Column(Integer)
    not_out = Column(Boolean, default=True)
    is_batting = Column(Boolean, default=False)
    is_bowling = Column(Boolean, default=False)

# Patnership Table
class Partnership(Base):
    __tablename__ = 'partnerships'
    partnership_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    player1_id = Column(Integer, ForeignKey('players.player_id'))
    player2_id = Column(Integer, ForeignKey('players.player_id'))
    runs_scored = Column(Integer)
    balls_faced = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    out = Column(String(20))
    strike_rate = Column(Float)

class Fielding(Base):
    __tablename__ = 'fielding'
    fielding_id = Column(Integer, primary_key=True)
    out_player_id = Column(Integer, ForeignKey('players.player_id'))
    fielder_id = Column(Integer, ForeignKey('players.player_id'))
    bowler_id = Column(Integer, ForeignKey('players.player_id'))
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    innings_id = Column(Integer, ForeignKey('innings.innings_id'))
    over_number = Column(Integer)
    ball_number = Column(Integer)
    out_type = Column(String(20))



