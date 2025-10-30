import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import streamlit as st

# Load environment variables
load_dotenv()

@st.cache_resource
def get_snowflake_connection():
    """Create and cache Snowflake connection using private key authentication."""

    # Try to load from Streamlit secrets first (for cloud deployment)
    if "snowflake" in st.secrets:
        # Cloud deployment - read from secrets
        if "private_key" in st.secrets.snowflake:
            # Private key is stored directly in secrets
            private_key = serialization.load_pem_private_key(
                st.secrets.snowflake.private_key.encode(),
                password=None,
                backend=default_backend()
            )
        else:
            # Fallback to file path in secrets
            key_path = st.secrets.snowflake.private_key_path
            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )

        account = st.secrets.snowflake.account
        user = st.secrets.snowflake.user
        warehouse = st.secrets.snowflake.warehouse
        database = st.secrets.snowflake.database
        schema = st.secrets.snowflake.schema
    else:
        # Local deployment - read from .env file
        key_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH')
        with open(key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        database = os.getenv('SNOWFLAKE_DATABASE')
        schema = os.getenv('SNOWFLAKE_SCHEMA')

    # Get private key in bytes
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        private_key=private_key_bytes,
        warehouse=warehouse,
        database=database,
        schema=schema
    )

    return conn

@st.cache_data(ttl=604800)  # Cache for 1 week (604800 seconds)
def get_team_stats():
    """
    Fetch and calculate team statistics from Snowflake.
    Returns a DataFrame with team-level xG statistics, rankings, and match results.
    """
    conn = get_snowflake_connection()

    query = """
    WITH match_results AS (
        SELECT
            "matchId",
            "homeSquadName",
            "awaySquadName",
            SUM(CASE WHEN "squadName" = "homeSquadName" AND GOALS = 1 THEN 1 ELSE 0 END)
                + SUM(CASE WHEN "squadName" = "awaySquadName" AND OWNGOALS = 1 THEN 1 ELSE 0 END) as home_goals,
            SUM(CASE WHEN "squadName" = "awaySquadName" AND GOALS = 1 THEN 1 ELSE 0 END)
                + SUM(CASE WHEN "squadName" = "homeSquadName" AND OWNGOALS = 1 THEN 1 ELSE 0 END) as away_goals
        FROM IMPECT_EVENTS_STAGING
        WHERE GOALS IS NOT NULL OR OWNGOALS IS NOT NULL
        GROUP BY "matchId", "homeSquadName", "awaySquadName"
    ),
    team_points AS (
        SELECT team, SUM(points) as total_points, COUNT(*) as matches_played
        FROM (
            SELECT
                "homeSquadName" as team,
                CASE
                    WHEN home_goals > away_goals THEN 3
                    WHEN home_goals = away_goals THEN 1
                    ELSE 0
                END as points
            FROM match_results
            UNION ALL
            SELECT
                "awaySquadName" as team,
                CASE
                    WHEN away_goals > home_goals THEN 3
                    WHEN home_goals = away_goals THEN 1
                    ELSE 0
                END as points
            FROM match_results
        )
        GROUP BY team
    ),
    team_stats AS (
        SELECT
            "squadName" as team,

            -- Goals
            SUM(CASE WHEN GOALS = 1 THEN 1 ELSE 0 END) as goals,

            -- xG (attacking)
            SUM(COALESCE(SHOT_XG, 0)) as xg,

            -- Set piece vs open play (attacking)
            SUM(CASE
                WHEN SHOT_XG > 0 AND "phase" = 'SET_PIECE'
                THEN COALESCE(SHOT_XG, 0)
                ELSE 0
            END) as set_piece_xg,
            SUM(CASE
                WHEN GOALS = 1 AND "phase" = 'SET_PIECE'
                THEN 1
                ELSE 0
            END) as set_piece_goals,

            -- Count matches for per 90 calculation
            COUNT(DISTINCT "matchId") as matches_played

        FROM IMPECT_EVENTS_STAGING
        WHERE "squadName" IS NOT NULL
            AND "squadName" != 'nan'
        GROUP BY "squadName"
    ),
    opponent_stats AS (
        SELECT
            opponent_team as team,

            -- Goals conceded
            SUM(CASE WHEN GOALS = 1 THEN 1 ELSE 0 END) as goals_against,

            -- xGA (defensive)
            SUM(COALESCE(SHOT_XG, 0)) as xga,

            -- Set piece vs open play (defensive)
            SUM(CASE
                WHEN SHOT_XG > 0 AND "phase" = 'SET_PIECE'
                THEN COALESCE(SHOT_XG, 0)
                ELSE 0
            END) as set_piece_xga,
            SUM(CASE
                WHEN GOALS = 1 AND "phase" = 'SET_PIECE'
                THEN 1
                ELSE 0
            END) as set_piece_goals_against

        FROM (
            SELECT
                "homeSquadName" as opponent_team,
                "squadName",
                GOALS,
                SHOT_XG,
                "phase"
            FROM IMPECT_EVENTS_STAGING
            WHERE "squadName" = "awaySquadName"
                AND "squadName" IS NOT NULL
                AND "squadName" != 'nan'

            UNION ALL

            SELECT
                "awaySquadName" as opponent_team,
                "squadName",
                GOALS,
                SHOT_XG,
                "phase"
            FROM IMPECT_EVENTS_STAGING
            WHERE "squadName" = "homeSquadName"
                AND "squadName" IS NOT NULL
                AND "squadName" != 'nan'
        )
        GROUP BY opponent_team
    )
    SELECT
        ts.team,
        ts.matches_played,
        COALESCE(tp.total_points, 0) as total_points,
        COALESCE(tp.total_points, 0) / NULLIF(ts.matches_played, 0) as points_per_game,

        -- Attacking stats
        ts.goals,
        ts.xg,
        ts.xg - ts.set_piece_xg as open_play_xg,
        ts.set_piece_xg,
        ts.goals - ts.set_piece_goals as open_play_goals,
        ts.set_piece_goals,
        ts.xg / NULLIF(ts.matches_played, 0) as xg_per_90,
        CASE WHEN ts.xg > 0 THEN ts.goals / ts.xg ELSE 0 END as xg_conversion,

        -- Defensive stats
        COALESCE(os.goals_against, 0) as goals_against,
        COALESCE(os.xga, 0) as xga,
        COALESCE(os.xga, 0) - COALESCE(os.set_piece_xga, 0) as open_play_xga,
        COALESCE(os.set_piece_xga, 0) as set_piece_xga,
        COALESCE(os.goals_against, 0) - COALESCE(os.set_piece_goals_against, 0) as open_play_goals_against,
        COALESCE(os.set_piece_goals_against, 0) as set_piece_goals_against,
        COALESCE(os.xga, 0) / NULLIF(ts.matches_played, 0) as xga_per_90,
        CASE WHEN os.xga > 0 THEN os.goals_against / os.xga ELSE 0 END as xga_conversion,

        -- xGD
        ts.xg - COALESCE(os.xga, 0) as xgd,
        (ts.xg - COALESCE(os.xga, 0)) / NULLIF(ts.matches_played, 0) as xgd_per_90

    FROM team_stats ts
    LEFT JOIN opponent_stats os ON ts.team = os.team
    LEFT JOIN team_points tp ON ts.team = tp.team
    ORDER BY xg DESC
    """

    df = pd.read_sql(query, conn)

    # Calculate rankings
    df['goals_rank'] = df['GOALS'].rank(ascending=False, method='min').astype(int)
    df['xg_rank'] = df['XG'].rank(ascending=False, method='min').astype(int)
    df['open_play_xg_rank'] = df['OPEN_PLAY_XG'].rank(ascending=False, method='min').astype(int)
    df['set_piece_xg_rank'] = df['SET_PIECE_XG'].rank(ascending=False, method='min').astype(int)
    df['set_piece_goals_rank'] = df['SET_PIECE_GOALS'].rank(ascending=False, method='min').astype(int)
    df['xg_per_90_rank'] = df['XG_PER_90'].rank(ascending=False, method='min').astype(int)
    df['xg_conversion_rank'] = df['XG_CONVERSION'].rank(ascending=False, method='min').astype(int)

    df['goals_against_rank'] = df['GOALS_AGAINST'].rank(ascending=True, method='min').astype(int)
    df['xga_rank'] = df['XGA'].rank(ascending=True, method='min').astype(int)
    df['open_play_xga_rank'] = df['OPEN_PLAY_XGA'].rank(ascending=True, method='min').astype(int)
    df['set_piece_xga_rank'] = df['SET_PIECE_XGA'].rank(ascending=True, method='min').astype(int)
    df['set_piece_goals_against_rank'] = df['SET_PIECE_GOALS_AGAINST'].rank(ascending=True, method='min').astype(int)
    df['xga_per_90_rank'] = df['XGA_PER_90'].rank(ascending=True, method='min').astype(int)
    df['xga_conversion_rank'] = df['XGA_CONVERSION'].rank(ascending=True, method='min').astype(int)

    return df

@st.cache_data(ttl=604800)  # Cache for 1 week
def get_match_by_match_data(team_name):
    """
    Get match-by-match xG, xGA, and points data for a specific team.
    """
    conn = get_snowflake_connection()

    # Get all matches for the team with proper team stats
    query = f"""
    WITH all_matches AS (
        SELECT DISTINCT
            "matchId",
            "dateTime",
            "homeSquadName",
            "awaySquadName"
        FROM IMPECT_EVENTS_STAGING
        WHERE "homeSquadName" = '{team_name}' OR "awaySquadName" = '{team_name}'
    ),
    match_stats AS (
        SELECT
            "matchId",
            "squadName",
            SUM(COALESCE(SHOT_XG, 0)) as xg,
            SUM(CASE WHEN GOALS = 1 THEN 1 ELSE 0 END) as goals,
            SUM(CASE WHEN OWNGOALS = 1 THEN 1 ELSE 0 END) as own_goals
        FROM IMPECT_EVENTS_STAGING
        WHERE "matchId" IN (SELECT "matchId" FROM all_matches)
            AND "squadName" IS NOT NULL
            AND "squadName" != 'nan'
        GROUP BY "matchId", "squadName"
    ),
    match_goals AS (
        SELECT
            m."matchId",
            COALESCE(home_stats.goals, 0) + COALESCE(away_stats.own_goals, 0) as home_goals,
            COALESCE(away_stats.goals, 0) + COALESCE(home_stats.own_goals, 0) as away_goals,
            COALESCE(home_stats.xg, 0) as home_xg,
            COALESCE(away_stats.xg, 0) as away_xg
        FROM all_matches m
        LEFT JOIN match_stats home_stats
            ON m."matchId" = home_stats."matchId"
            AND home_stats."squadName" = m."homeSquadName"
        LEFT JOIN match_stats away_stats
            ON m."matchId" = away_stats."matchId"
            AND away_stats."squadName" = m."awaySquadName"
    )
    SELECT
        m."matchId",
        m."dateTime",
        m."homeSquadName",
        m."awaySquadName",
        CASE
            WHEN m."homeSquadName" = '{team_name}' THEN m."awaySquadName"
            ELSE m."homeSquadName"
        END as opponent,
        CASE
            WHEN m."homeSquadName" = '{team_name}' THEN 'H'
            ELSE 'A'
        END as venue,
        mg.home_xg,
        mg.home_goals,
        mg.away_xg,
        mg.away_goals
    FROM all_matches m
    INNER JOIN match_goals mg ON m."matchId" = mg."matchId"
    ORDER BY m."dateTime"
    """

    df = pd.read_sql(query, conn)

    # Calculate team's xG, xGA, goals for/against from team's perspective
    df['XG_FOR'] = df.apply(lambda row: row['HOME_XG'] if row['VENUE'] == 'H' else row['AWAY_XG'], axis=1)
    df['XG_AGAINST'] = df.apply(lambda row: row['AWAY_XG'] if row['VENUE'] == 'H' else row['HOME_XG'], axis=1)
    df['GOALS_FOR'] = df.apply(lambda row: row['HOME_GOALS'] if row['VENUE'] == 'H' else row['AWAY_GOALS'], axis=1)
    df['GOALS_AGAINST'] = df.apply(lambda row: row['AWAY_GOALS'] if row['VENUE'] == 'H' else row['HOME_GOALS'], axis=1)

    # Calculate points
    df['POINTS'] = df.apply(lambda row: 3 if row['GOALS_FOR'] > row['GOALS_AGAINST']
                            else (1 if row['GOALS_FOR'] == row['GOALS_AGAINST'] else 0), axis=1)

    # Add match number and date label
    df['match_number'] = range(1, len(df) + 1)
    df['match_label'] = df.apply(lambda row: f"{row['match_number']}: {row['OPPONENT']}", axis=1)

    # Calculate rolling averages (right-aligned, includes current match)
    df['xg_rolling_5'] = df['XG_FOR'].rolling(window=5, min_periods=1).mean()
    df['xga_rolling_5'] = df['XG_AGAINST'].rolling(window=5, min_periods=1).mean()

    return df
