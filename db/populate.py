from datetime import datetime
import json
from data_models.schema import Tournament, Match, Team, Innings, Player, Ball, PlayerStatsInnings, PlayerStatsOver, PlayerVsPlayerInnings, Stadium, Partnership, Fielding

class MatchData:
    def __init__(self):
        self.tourament_id = None
        self.stadium_id = None
        self.team_ids = {}
        self.player_id_map = {}
        self.match_id = None

class ProcessMatchData:

    def __init__(self, filePath: str, session):
        self.filePath = filePath
        self.session = session
        self.curr_data = MatchData()
    
    def process(self):

        with open(self.filePath, 'r') as file:
            data = json.load(file)
        
        event = data["info"].get("event", {})
        tournament_name = str(event.get("name", "default")) + " " + str(data["info"]["season"])

        #search for the tournament with in database if not found create a new one
        self.curr_data.tourament_id = self.try_create_tournament(tournament_name, data)

        #Stadium
        self.curr_data.stadium_id = self.try_create_stadium(data['info']['venue'], data= data)

        #Team
        self.curr_data.team_ids = self.try_create_teams(data)

        #Players, can contain referees and umpires as well
        self.curr_data.player_id_map = self.try_create_players(data)
        
        #Match
        self.curr_data.match_id = self.try_create_match(data)

        innings_num = 1

        for innings in data['innings']:
            self.try_create_innings(innings, innings_num)
            innings_num += 1

        #TODO: add match stats

    # Initialize player stats if not already present
    def init_player_innings_stats(self, player_id, player_innings_stats):
        if player_id not in player_innings_stats:
            stats = {
                "runs_scored": 0,
                "balls_faced": 0,
                "fours": 0,
                "sixes": 0,
                "not_out": True,
                "did_not_bat": True,
                "runs_conceded": 0,
                "balls_bowled": 0,
                "fours_conceded": 0,
                "sixes_conceded": 0,
                "wickets_taken": 0,
                "did_not_bowl": True
            }
            player_innings_stats[player_id] = stats

    def init_player_over_stats(self, player_id, over_number, player_over_stats, is_batting = False, is_bowling = False):
        if player_id not in player_over_stats:
            player_over_stats[player_id] = {}
        
        if over_number not in player_over_stats[player_id]:
            stats = {
                "overs_number": over_number,
                "runs_scored": 0,
                "balls_faced": 0,
                "fours": 0,
                "sixes": 0,
                "outs": 0,
                "not_out": True,
                "balls_bowled": 0,
                "runs_conceded": 0,
                "wickets_taken": 0,
                "fours_conceded": 0,
                "sixes_conceded": 0,
                "is_batting": is_batting,
                "is_bowling": is_bowling
            }
            player_over_stats[player_id][over_number] = stats


    def init_player_vs_player_innings(self, pvpId, player_vs_player_innings):
        if pvpId not in player_vs_player_innings:
            stats = {
                "runs_scored": 0,
                "balls_faced": 0,
                "fours": 0,
                "sixes": 0,
                "outs": 0,
                "overs_bowled": 0,
                "runs_conceded": 0,
                "fours_conceded": 0,
                "sixes_conceded": 0,
                "wickets_taken": 0,
            }
            player_vs_player_innings[pvpId] = stats

    def init_partnership(self, partnershipId, partnerships):
        if partnershipId not in partnerships:
            stats = {
                "runs": 0,
                "balls": 0,
                "fours": 0,
                "sixes": 0,
                "out": False
            }
            partnerships[partnershipId] = stats



    def try_create_innings(self, innings: dict, innings_num: int):

        batting_team_id = self.curr_data.team_ids[innings["team"]]

        #find the bowling team id, the team that is not the batting team
        team_ids_list = list(self.curr_data.team_ids.values())
        bowling_team_id = team_ids_list[0] if team_ids_list[0] != batting_team_id else team_ids_list[1]


        runs_scored = 0
        wickets_lost = 0
        total_deliveries = 0
        overs_played = 0
        total_extras = {
            "byes": 0,
            "legbyes": 0,
            "wides": 0,
            "noballs": 0,
            "penalty": 0
        }
        fall_of_wickets = {
            "wickets": [],
            "runs": []
        }

        target = innings.get("target")
        declared = innings.get("declared")
        forfeited = innings.get("forfeited")
        powerplay = innings.get("powerplay")
        miscounted_overs = innings.get("miscounted_overs")
        super_over = innings.get("super_over", False)

        #Player innings stats
        player_innings_stats = {}

        #player vs player innings stats, key batter_id_bowler_id
        player_vs_player_innings = {}

        #partnership stats
        partnerships = {}

        fielding_stats = []
        ball_data = []

        powerplay_overs = innings.get("powerplay_overs", [])

        for over in innings["overs"]:
            delivery_num = 1

            over_num = over["over"]

            #player in over stats
            player_over_stats = {}

            for ball in over["deliveries"]:
                batter_id = self.curr_data.player_id_map[ball["batter"]]
                bowler_id = self.curr_data.player_id_map[ball["bowler"]]
                non_striker_id = self.curr_data.player_id_map[ball["non_striker"]]

                partnershipId = self.partnership_id(batter_id, non_striker_id)
                playerVplayerId = self.player_v_player_id(batter_id, bowler_id)
                
                # Initialize stats for all players in this delivery
                self.init_player_innings_stats(batter_id, player_innings_stats)
                self.init_player_innings_stats(non_striker_id, player_innings_stats)
                self.init_player_innings_stats(bowler_id, player_innings_stats)
                
                self.init_player_vs_player_innings(playerVplayerId, player_vs_player_innings)

                self.init_player_over_stats(batter_id, over_num, player_over_stats, is_batting = True)
                self.init_player_over_stats(bowler_id, over_num, player_over_stats, is_bowling = False)
                self.init_player_over_stats(non_striker_id, over_num, player_over_stats, is_batting = True)

                self.init_partnership(partnershipId, partnerships)

                #runs first
                runs = ball["runs"]

                batter_runs = runs["batter"]
                extra_runs = runs["extras"]
                total_runs = runs["total"]

                is_batter_four = batter_runs == 4 and runs.get("non_boundary", False) == False
                is_batter_six = batter_runs == 6 and runs.get("non_boundary", False) == False

                is_extra_four = extra_runs == 4 and runs.get("non_boundary", False) == False
                is_extra_six = extra_runs == 6 and runs.get("non_boundary", False) == False

                extras = ball.get("extras", None)

                is_valid_ball = True

                #batter
                player_innings_stats[batter_id]["did_not_bat"] = False
                player_innings_stats[non_striker_id]["did_not_bat"] = False
                player_innings_stats[batter_id]["runs_scored"] += batter_runs
                player_innings_stats[batter_id]["balls_faced"] += 1
                player_innings_stats[batter_id]["fours"] += 1 if is_batter_four else 0
                player_innings_stats[batter_id]["sixes"] += 1 if is_batter_six else 0

                #bowler
                player_innings_stats[bowler_id]["did_not_bowl"] = False
                player_innings_stats[bowler_id]["runs_conceded"] += batter_runs
                player_innings_stats[bowler_id]["fours_conceded"] += 1 if is_batter_four else 0
                player_innings_stats[bowler_id]["sixes_conceded"] += 1 if is_batter_six else 0

                if extras is not None:
                    if extras.get("wides", 0) > 0:
                        player_innings_stats[bowler_id]["runs_conceded"] += extras["wides"]
                        is_valid_ball = False
                    if extras.get("noballs", 0) > 0:
                        player_innings_stats[bowler_id]["runs_conceded"] += extras["noballs"]
                        is_valid_ball = False

                    for extra_type, extra_runs in extras.items():
                        total_extras[extra_type] += extra_runs #add to total extras
                    
                
                if is_valid_ball:
                    player_innings_stats[bowler_id]["balls_bowled"] += 1
                    delivery_num += 1

                #player vs player innings
                player_vs_player_innings[playerVplayerId]["runs_scored"] += batter_runs
                player_vs_player_innings[playerVplayerId]["balls_faced"] += 1
                player_vs_player_innings[playerVplayerId]["fours"] += 1 if is_batter_four else 0
                player_vs_player_innings[playerVplayerId]["sixes"] += 1 if is_batter_six else 0

                #patnership
                partnerships[partnershipId]["runs"] += batter_runs
                partnerships[partnershipId]["balls"] += 1
                partnerships[partnershipId]["fours"] += 1 if is_batter_four else 0
                partnerships[partnershipId]["sixes"] += 1 if is_batter_six else 0

                #player over stats
                player_over_stats[batter_id][over_num]["runs_scored"] += batter_runs
                player_over_stats[batter_id][over_num]["balls_faced"] += 1
                player_over_stats[batter_id][over_num]["fours"] += 1 if is_batter_four else 0
                player_over_stats[batter_id][over_num]["sixes"] += 1 if is_batter_six else 0

                wickets = ball.get("wicket", None)

                runs_scored += total_runs
                total_deliveries += 1 if is_valid_ball else 0

                #follow of wickets

                if wickets is not None:
                    for wicket in wickets:
                        wicket_kind = wicket["kind"]
                        player_out = self.curr_data.player_id_map[wicket["player_out"]]


                        if wicket_kind != "retired hurt":
                            wickets_lost += 1
                            fall_of_wickets["wickets"].append(wickets_lost)
                            fall_of_wickets["runs"].append(runs_scored)

                        match wicket_kind:
                            case "caught" | "caught and bowled" | "stumped":
                                partnerships[partnershipId]["out"] = True
                                player_innings_stats[batter_id]["not_out"] = False
                                player_over_stats[batter_id][over_num]["not_out"] = False
                                player_innings_stats[bowler_id]["wickets_taken"] += 1
                                player_over_stats[bowler_id][over_num]["wickets_taken"] += 1
                                player_vs_player_innings[playerVplayerId]["outs"] += 1

                                if wicket_kind == "caught and bowled":
                                    fielding_stats.append({
                                        "fielder": bowler_id,
                                        "out_type": "caught and bowled",
                                        "over_number": over_num,
                                        "ball_number": delivery_num,
                                        "out_player_id": player_out,
                                        "bowler_id": bowler_id
                                    })

                                    player_innings_stats[bowler_id]["catches"] += 1

                                else:
                                    for fielder in wicket["fielders"]:
                                        fielder_id = self.curr_data.player_id_map[fielder]
                                        fielding_stats.append({
                                            "fielder": fielder_id,
                                            "out_type": wicket_kind,
                                            "over_number": over_num,
                                            "ball_number": delivery_num,
                                            "out_player_id": player_out,
                                            "bowler_id": bowler_id
                                        })

                            case "bowled" | "lbw" | "hit wicket":
                                partnerships[partnershipId]["out"] = True
                                player_innings_stats[batter_id]["not_out"] = False
                                player_over_stats[batter_id][over_num]["not_out"] = False
                                player_innings_stats[bowler_id]["wickets_taken"] += 1
                                player_over_stats[bowler_id][over_num]["wickets_taken"] += 1
                                player_vs_player_innings[playerVplayerId]["outs"] += 1



                                
                            case "run out":
                                partnerships[partnershipId]["out"] = True
                                player_innings_stats[player_out]["not_out"] = False
                                player_over_stats[player_out][over_num]["not_out"] = False


                                for fielder in wicket["fielders"]:
                                    fielder_id = self.curr_data.player_id_map[fielder]
                                    fielding_stats.append({
                                        "fielder": fielder_id,
                                        "out_type": wicket_kind,
                                        "over_number": over_num,
                                        "ball_number": delivery_num,
                                        "out_player_id": player_out,
                                        "bowler_id": bowler_id
                                    })


                            case "retired hurt":
                                # do nothing
                                pass
    
                            case _:
                                partnerships[partnershipId]["out"] = True
                                player_innings_stats[player_out]["not_out"] = False
                                player_over_stats[player_out][over_num]["not_out"] = False


                is_powerplay, powerplay_type = self.is_powerplay(over_num, delivery_num, powerplay_overs)

                ball_data.append({
                    "ball_number": delivery_num,
                    "batsman_id": batter_id,
                    "bowler_id": bowler_id,
                    "non_striker_id": non_striker_id,
                    "runs": json.dumps(runs),
                    "extras": json.dumps(extras),
                    "wicket": json.dumps(wickets),
                    "replacement": json.dumps(ball.get("replacement", None)),
                    "review": json.dumps(ball.get("review", None)),
                    "is_powerplay": is_powerplay,
                    "powerplay_type": powerplay_type
                })

        #Innings
        overs_played = total_deliveries / 6 + (total_deliveries % 6) / 10

        innings = Innings(
            match_id = self.curr_data.match_id,
            batting_team_id = batting_team_id,
            bowling_team_id = bowling_team_id,
            runs_scored = runs_scored,
            wickets_lost = wickets_lost,
            total_deliveries = total_deliveries,
            overs_played = overs_played,
            extras = json.dumps(total_extras),
            fall_of_wickets = json.dumps(fall_of_wickets),
            target = target,
            declared = declared,
            forfeited = forfeited,
            powerplay = powerplay,
            miscounted_overs = miscounted_overs,
            super_over = super_over
        )

        self.session.add(innings)
        self.session.commit()

        #PlayerStatsInnings
        for player_id, stats in player_innings_stats.items():
            player_stats = PlayerStatsInnings(
                player_id = player_id,
                match_id = self.curr_data.match_id,
                innings_id = innings.innings_id,
                runs_scored = stats["runs_scored"],
                balls_faced = stats["balls_faced"],
                fours = stats["fours"],
                sixes = stats["sixes"],
                strike_rate = (stats["runs_scored"] / stats["balls_faced"]) * 100 if stats["balls_faced"] > 0 else 0,
                not_out = stats.get("not_out", True),
                did_not_bat = stats.get("did_not_bat"),
                did_not_bowl = stats.get("did_not_bowl"),
                balls_bowled = stats.get("balls_bowled"),
                wickets_taken = stats.get("wickets_taken"),
                runs_conceded = stats.get("runs_conceded"),
                economy = stats.get("runs_conceded") / stats.get("balls_bowled")*6 if stats.get("balls_bowled", 0) > 0 else 0,
                catches = stats.get("catches"), #TODO: add catches
                run_outs = stats.get("run_outs"), #TODO: add run_outs
                stumpings = stats.get("stumpings") #TODO: add stumpings
            )

            self.session.add(player_stats)


        # PlayerStatsOver
        for player_id, over_stats_dict in player_over_stats.items():
            for over_number, stats in over_stats_dict.items():
                player_over = PlayerStatsOver(
                    player_id=player_id,
                    match_id=self.curr_data.match_id,
                    innings_id=innings.innings_id,
                    over_number=over_number,  # Extracting over number from the dictionary key
                    runs_scored=stats["runs_scored"],
                    balls_faced=stats["balls_faced"],
                    strike_rate=(stats["runs_scored"] / stats["balls_faced"]) * 100 if stats["balls_faced"] > 0 else 0,
                    fours=stats["fours"],
                    sixes=stats["sixes"],
                    not_out=stats.get("not_out", True),
                    balls_bowled=stats.get("balls_bowled", 0),
                    runs_conceded=stats.get("runs_conceded", 0),
                    wickets_taken=stats.get("wickets_taken", 0),
                    economy=(stats.get("runs_conceded", 0) / stats.get("balls_bowled", 1)) * 6 if stats.get("balls_bowled", 0) > 0 else 0,
                    fours_conceded=stats.get("fours_conceded", 0),
                    sixes_conceded=stats.get("sixes_conceded", 0),
                    is_batting=stats.get("is_batting", False),
                    is_bowling=stats.get("is_bowling", False)
                )

                self.session.add(player_over)



        #PlayerVsPlayerInnings
        for player_id, stats in player_vs_player_innings.items():
            player_vs_player = PlayerVsPlayerInnings(
                batsman_id = player_id.split("_")[0],
                bowler_id = player_id.split("_")[1],
                match_id = self.curr_data.match_id,
                innings_id = innings.innings_id,
                runs_scored = stats["runs_scored"],
                balls_faced = stats["balls_faced"],
                fours = stats["fours"],
                sixes = stats["sixes"],
                strike_rate = (stats["runs_scored"] / stats["balls_faced"]) * 100 if stats["balls_faced"] > 0 else 0,
                outs = stats["outs"],
                overs_bowled = stats["overs_bowled"],
                runs_conceded = stats["runs_conceded"],
                fours_conceded = stats["fours_conceded"],
                sixes_conceded = stats["sixes_conceded"],
                wickets_taken = stats["wickets_taken"],
                economy = stats["runs_conceded"] / stats["overs_bowled"]*6 if stats["overs_bowled"] > 0 else 0
            )

            self.session.add(player_vs_player)


        #Partnerships
        for partnership_id, stats in partnerships.items():
            partnership = Partnership(
                match_id = self.curr_data.match_id,
                innings_id = innings.innings_id,
                player1_id = partnership_id.split("_")[0],
                player2_id = partnership_id.split("_")[1],
                runs_scored = stats["runs"],
                balls_faced = stats["balls"],
                fours = stats["fours"],
                sixes = stats["sixes"],
                out = stats["out"],
                strike_rate = (stats["runs"] / stats["balls"]) * 100 if stats["balls"] > 0 else 0
            )

            self.session.add(partnership)
        

        #Fielding
        for fielding in fielding_stats:
            fielding = Fielding(
                fielder_id = fielding["fielder"],
                out_type = fielding["out_type"],
                over_number = fielding["over_number"],
                ball_number = fielding["ball_number"],
                out_player_id = fielding["out_player_id"],
                bowler_id = fielding["bowler_id"],
                match_id = self.curr_data.match_id,
                innings_id = innings.innings_id
            )

            self.session.add(fielding)

        #Ball
        for ball in ball_data:
            ball = Ball(
                ball_number = ball["ball_number"],
                innings_id = innings.innings_id,
                match_id = self.curr_data.match_id,
                batsman_id = ball["batsman_id"],
                bowler_id = ball["bowler_id"],
                non_striker_id = ball["non_striker_id"],
                runs = ball["runs"],
                extras = ball["extras"],
                wicket = ball["wicket"],
                replacement = ball["replacement"],
                review = ball["review"],
                is_powerplay = ball["is_powerplay"],
                powerplay_type = ball["powerplay_type"]
            )

            self.session.add(ball)

        self.session.commit()





    def is_powerplay(self, over_num: int, delivery_num, powerplay_overs) -> tuple[bool, str]:
        if not powerplay_overs:
            return False, None

        for powerplay in powerplay_overs:
            start_over, start_del = powerplay["from"].split(".")
            end_over, to_del = powerplay["to"].split(".")

            if over_num >= start_over and over_num <= end_over:
                if over_num == start_over and delivery_num >= start_del:
                    return True, powerplay["type"]
                elif over_num == end_over and delivery_num <= to_del:
                    return True, powerplay["type"]
                elif over_num > start_over and over_num < end_over:
                    return True, powerplay["type"]
                
        return False, None


        


    
    def try_create_tournament(self, tournament_name:str, data: dict) -> int:
        tournament = self.session.query(Tournament).filter(Tournament.name == tournament_name).first()

        if tournament is None:
            tournament = Tournament(
                name=tournament_name,
                gender = data["info"]["gender"],
                format = data["info"]["match_type"],
                season = data["info"]["season"]
            )
            
            self.session.add(tournament)
            self.session.commit()

        #need to return the tournament_id
        return tournament.tournament_id



    def try_create_stadium(self, stadium_name: str, data: dict) -> int:
        stadium = self.session.query(Stadium).filter(Stadium.name == stadium_name).first()
        
        if stadium is None:
            stadium = Stadium(
                name=stadium_name,
                city = data["info"].get("city", None),
            )
            self.session.add(stadium)
            self.session.commit()
        
        return stadium.stadium_id
    
    def try_create_teams(self, data: dict):
        assert len(data["info"]["teams"]) == 2

        team1Name  = data["info"]["teams"][0]
        team2Name = data["info"]["teams"][1]

        team1 = self.session.query(Team).filter(Team.name == team1Name).first()
        team2 = self.session.query(Team).filter(Team.name == team2Name).first()

        if team1 is None:
            team1 = Team(
                name = team1Name,
                gender = data["info"]["gender"]
            )
            self.session.add(team1)

        if team2 is None:
            team2 = Team(
                name = team2Name,
                gender = data["info"]["gender"]
            )
            self.session.add(team2)

        self.session.commit()

        return {
            team1Name: team1.team_id,
            team2Name: team2.team_id
        }
    
    def try_create_players(self, data: dict):
        player_id_map = {}

        for player_name, player_external_id in data["info"]["registry"]["people"].items():
            player = self.session.query(Player).filter(Player.external_id == player_external_id).first()

            if player is None:
                player = Player(
                    external_id = player_external_id,
                    name = player_name,
                    gender = data["info"]["gender"],
                )
                self.session.add(player)

        self.session.commit()

        for player_name, player_external_id in data["info"]["registry"]["people"].items():
            player_id_map[player_name] = self.session.query(Player).filter(Player.external_id == player_external_id).first().player_id


        return player_id_map
    
    def try_create_match(self, data: dict):

        team_ids_list = list(self.curr_data.team_ids.values())
        team1_id, team2_id = team_ids_list[0], team_ids_list[1]


        match = Match(
            balls_per_over = data["info"].get("balls_per_over", 6),
            stadium_id = self.curr_data.stadium_id,
            tournament_id = self.curr_data.tourament_id,
            tournament_match_details = json.dumps(data["info"].get("event", {})),  # Ensure JSON format
            gender = data["info"]["gender"],
            match_dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in data["info"]["dates"]],
            match_type = data["info"]["match_type"],
            match_type_number = data["info"].get("match_type_number"),
            season = data["info"]["season"],
            team1_id = team1_id,
            team2_id = team2_id,
            outcome = json.dumps(data["info"].get("outcome", {})),
            toss = json.dumps(data["info"].get("toss", {})),
            man_of_the_match = self.map_player_names_to_ids(data["info"].get("player_of_match", [])) or None,
            team_type = data["info"].get("team_type"),
            players = self.map_player_field(data["info"]["players"]),
            bowl_out = json.dumps(data["info"].get("bowl_out", None)),
            missing = json.dumps(data["info"].get("missing", None)),
            officials = json.dumps(data["info"].get("officials", None)),
            super_subs = json.dumps(self.map_player_field(data["info"].get("supersubs", {}))) if "supersubs" in data["info"] else None,
        )

        self.session.add(match)
        self.session.commit()

        return match.match_id

    
    def map_player_names_to_ids(self, player_names: list):
        return [self.curr_data.player_id_map[player] for player in player_names]


    def map_player_field(self, data) -> dict:
        player_data = {}

        for team, players in data.items():
            teamId = self.curr_data.team_ids[team]

            if isinstance(players, list):
                player_data[teamId] = self.map_player_names_to_ids(players)
            else:
                assert isinstance(players, str) and players is not None
                player_data[teamId] = [self.curr_data.player_id_map[players]]

        return player_data

    
    def player_v_player_id(self, batter_id: int, bowler_id: int) -> str:
        return f"{batter_id}_{bowler_id}"

    def partnership_id(self, batter1_id: int, batter2_id: int) -> str:
        if batter1_id < batter2_id:
            return f"{batter1_id}_{batter2_id}"
        else:
            return f"{batter2_id}_{batter1_id}"



            

        





