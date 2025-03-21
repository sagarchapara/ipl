from dataclasses import dataclass
from typing import List



@dataclass
class Player:
    name: str
    external_id: str

@dataclass
class Team:
    name: str
    team_id: str
    players: List[Player]

@dataclass
class Match:
    stadium: str
    tournament: str
    teams: List[Team]
    stadium_id: str
    tournament_id: str





class IplTeamFinder:


    def find_good_attributes(player_name: str, curr_team: Team, opposition_team: Team, match: Match):

        # What are the good attributes of a player?

        # 1. Total aggregate stats of the player + last 5 matches
        # 2. Player's aggregate performance against the opposition team + last 5 matches
        # 3. Player's aggregate performance against opposition team in last 5 matches
        # 4. Player's performance in the current stadium + last 5 matches in the stadium
        # 5. Player's performance in the current tournament + last 5 matches in the tournament
        # 6. Player's performance vs all the players in the opposition team, both aggregate and last 5 matches
        pass