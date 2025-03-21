def get_player_tournament_aggregate_and_last_n(player_id: int, tournament_id: int, last_n: int):
    query = """
        -- Total in tournament
        SELECT 'total' AS type, *
        FROM player_totals_by_tournament_mv
        WHERE player_id = %(player_id)s AND tournament_id = %(tournament_id)s

        UNION ALL

        -- Last %(last_n)s in tournament
        SELECT 'last_n' AS type, psi.*
        FROM player_stats_innings psi
        JOIN matches m ON psi.match_id = m.match_id
        WHERE psi.player_id = %(player_id)s AND m.tournament_id = %(tournament_id)s
          AND psi.match_id IN (
              SELECT match_id
              FROM matches
              WHERE tournament_id = %(tournament_id)s
              ORDER BY match_id DESC
              LIMIT %(last_n)s
          );
    """
    return query, {
        "player_id": player_id,
        "tournament_id": tournament_id,
        "last_n": last_n
    }

def get_player_stadium_aggregate_and_last_n(player_id: int, stadium_id: int, last_n: int):
    query = """
        -- Total in stadium
        SELECT 'total' AS type, *
        FROM player_totals_by_stadium_mv
        WHERE player_id = %(player_id)s AND stadium_id = %(stadium_id)s

        UNION ALL

        -- Last %(last_n)s in stadium
        SELECT 'last_n' AS type, psi.*
        FROM player_stats_innings psi
        JOIN matches m ON psi.match_id = m.match_id
        WHERE psi.player_id = %(player_id)s AND m.stadium_id = %(stadium_id)s
          AND psi.match_id IN (
              SELECT match_id
              FROM matches
              WHERE stadium_id = %(stadium_id)s
              ORDER BY match_id DESC
              LIMIT %(last_n)s
          );
    """
    return query, {
        "player_id": player_id,
        "stadium_id": stadium_id,
        "last_n": last_n
    }

def get_player_opposition_aggregate_and_last_n(player_id: int, opponent_team_id: int, last_n: int):
    query = """
        -- Total vs opposition team
        SELECT 'total' AS type, *
        FROM player_totals_by_opposition_mv
        WHERE player_id = %(player_id)s AND opposition_team_id = %(opponent_team_id)s

        UNION ALL

        -- Last %(last_n)s vs opposition team
        SELECT 'last_n' AS type, psi.*
        FROM player_stats_innings psi
        JOIN matches m ON psi.match_id = m.match_id
        WHERE psi.player_id = %(player_id)s
          AND (m.team1_id = %(opponent_team_id)s OR m.team2_id = %(opponent_team_id)s)
          AND psi.match_id IN (
              SELECT match_id
              FROM player_stats_innings
              WHERE player_id = %(player_id)s
                AND match_id IN (
                    SELECT match_id FROM matches
                    WHERE team1_id = %(opponent_team_id)s OR team2_id = %(opponent_team_id)s
                )
              ORDER BY match_id DESC
              LIMIT %(last_n)s
          );
    """
    return query, {
        "player_id": player_id,
        "opponent_team_id": opponent_team_id,
        "last_n": last_n
    }

def get_player_totals_and_last_n_matches(player_id: int, last_n: int):
    query = """
        -- Total career aggregate
        SELECT 'total' AS type, * 
        FROM player_totals_mv 
        WHERE player_id = %(player_id)s

        UNION ALL

        -- Last %(last_n)s raw match-level rows
        SELECT 'last_n' AS type, *
        FROM player_stats_innings
        WHERE player_id = %(player_id)s
        ORDER BY match_id DESC
        LIMIT %(last_n)s;
    """
    return query, {"player_id": player_id, "last_n": last_n}

def get_player_vs_opponent_players_last_n(player_id: int, opponent_player_ids: list[int], last_n: int):
    query = """
        -- Total aggregated vs each opponent
        SELECT 'total' AS type, *
        FROM player_vs_player_totals_mv
        WHERE batsman_id = %(player_id)s
          AND bowler_id = ANY(%(opponent_player_ids)s)

        UNION ALL

        -- Last %(last_n)s match-wise head-to-heads
        SELECT 'last_n' AS type, *
        FROM player_vs_player_innings
        WHERE batsman_id = %(player_id)s
          AND bowler_id = ANY(%(opponent_player_ids)s)
        ORDER BY match_id DESC
        LIMIT %(last_n)s;
    """
    return query, {
        "player_id": player_id,
        "opponent_player_ids": opponent_player_ids,
        "last_n": last_n
    }



