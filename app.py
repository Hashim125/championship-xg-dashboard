import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import poisson
from database import get_team_stats, get_match_by_match_data
from badge_mapping import get_badge_path
from PIL import Image
from auth import check_password

# Page configuration
st.set_page_config(
    page_title="Championship xG Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check password before showing the app
if not check_password():
    st.stop()  # Stop execution if password is incorrect

def calculate_expected_points(xg_for, xg_against, max_goals=10):
    """
    Calculate expected points using Poisson distribution.

    Args:
        xg_for: Expected goals for the team
        xg_against: Expected goals against the team
        max_goals: Maximum number of goals to consider (default 10)

    Returns:
        Expected points for the match (0-3)
    """
    prob_win = 0
    prob_draw = 0

    # Calculate probability of each scoreline
    for home_goals in range(max_goals):
        for away_goals in range(max_goals):
            # Probability of this exact scoreline
            prob = poisson.pmf(home_goals, xg_for) * poisson.pmf(away_goals, xg_against)

            if home_goals > away_goals:
                prob_win += prob
            elif home_goals == away_goals:
                prob_draw += prob

    # Expected points = 3 * P(win) + 1 * P(draw) + 0 * P(loss)
    return 3 * prob_win + 1 * prob_draw

# Custom CSS for improved styling
st.markdown("""
    <style>
    /* Dark theme styling */
    .main {
        background-color: #0e1117;
        padding: 1rem 2rem;
    }

    /* Section headers */
    h1 {
        color: #ffffff;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        color: #ffffff;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        color: #fafafa;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
    }

    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #a0a0a0 !important;
        font-weight: 600 !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        font-size: 13px !important;
    }

    div[data-testid="stDataFrame"] > div {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] h2 {
        color: #ffffff;
        font-size: 1.3rem !important;
    }

    /* Select box styling */
    .stSelectbox label {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Caption styling */
    .caption {
        color: #808080 !important;
        font-size: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("⚽ Championship xG Analysis Dashboard")
st.markdown("---")

# Load data
with st.spinner('🔄 Loading data from Snowflake...'):
    df = get_team_stats()

# Sidebar - Team filter
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("")

selected_team = st.sidebar.selectbox(
    "Select Team",
    options=sorted(df['TEAM'].unique()),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 League Statistics")
st.sidebar.metric("Total Teams", len(df))
st.sidebar.metric("Matches Played", int(df['MATCHES_PLAYED'].iloc[0]))

# Get selected team data
team_data = df[df['TEAM'] == selected_team].iloc[0]

# Prepare images for layout - load badge for selected team
selected_badge_path = get_badge_path(selected_team)
if selected_badge_path:
    try:
        selected_badge = Image.open(selected_badge_path)
        # Resize for sidebar
        selected_badge = selected_badge.resize((120, 120), Image.Resampling.LANCZOS)
    except:
        selected_badge = None
else:
    selected_badge = None

# Display selected team badge in sidebar
if selected_badge:
    st.sidebar.markdown("---")
    st.sidebar.image(selected_badge, width=120)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 League Overview", "📈 Match Trends", "🏆 League Table", "⚖️ Team Comparison"])

with tab1:
    # Main layout - 65/35 split for better visualization space
    col1, col2 = st.columns([1.85, 1])

with col1:
    # Scatter Plot 1: xG Per 90 vs xGA Per 90
    st.subheader("📈 xG Per 90 vs xGA Per 90")

    fig1 = go.Figure()

    # Calculate consistent badge size based on axis range
    xg_range = df['XG_PER_90'].max() - df['XG_PER_90'].min()
    xga_range = df['XGA_PER_90'].max() - df['XGA_PER_90'].min()
    badge_size_1 = min(xg_range, xga_range) * 0.08  # 8% of smallest axis range

    # Add scatter points for all teams with badges as custom markers
    for idx, row in df.iterrows():
        team_name = row['TEAM']
        is_selected = (team_name == selected_team)

        badge_path = get_badge_path(team_name)

        # Determine marker style
        if is_selected:
            marker_color = '#FF4B4B'
            marker_size = 50
            marker_line_width = 3
        else:
            marker_color = '#4A90E2'
            marker_size = 35
            marker_line_width = 2

        # Try to load badge image
        custom_data = [team_name, row['XG_PER_90'], row['XGA_PER_90']]

        if badge_path:
            try:
                # Add badge as scatter marker using image with dynamic sizing
                fig1.add_layout_image(
                    dict(
                        source=Image.open(badge_path),
                        x=row['XG_PER_90'],
                        y=row['XGA_PER_90'],
                        xref="x",
                        yref="y",
                        sizex=badge_size_1,
                        sizey=badge_size_1,
                        xanchor="center",
                        yanchor="middle",
                        layer="above"
                    )
                )
            except:
                # Fallback to regular marker
                pass

        # Add invisible scatter point for hover
        fig1.add_trace(go.Scatter(
            x=[row['XG_PER_90']],
            y=[row['XGA_PER_90']],
            mode='markers',
            marker=dict(
                size=marker_size,
                color='rgba(0,0,0,0)',  # Transparent
                line=dict(width=0)
            ),
            hovertemplate=f'<b>{team_name}</b><br>xG/90: {row["XG_PER_90"]:.2f}<br>xGA/90: {row["XGA_PER_90"]:.2f}<extra></extra>',
            showlegend=False,
            name=team_name
        ))

    # Add y=x line (perfect balance line)
    # Teams above the line: better defense (lower xGA)
    # Teams below the line: better attack (higher xG)
    min_val = min(df['XG_PER_90'].min(), df['XGA_PER_90'].min())
    max_val = max(df['XG_PER_90'].max(), df['XGA_PER_90'].max())
    fig1.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dash'),
        showlegend=False,
        hoverinfo='skip',
        name='Balance Line (y=x)'
    ))

    fig1.update_layout(
        xaxis_title="xG Per 90",
        yaxis_title="xGA Per 90",
        height=450,
        hovermode='closest',
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#0e1117',
        font=dict(color='white', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        margin=dict(l=60, r=20, t=40, b=60)
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Scatter Plot 2: xG Conversion vs xGA Conversion
    st.subheader("🎯 xG Conversion vs xGA Conversion")

    fig2 = go.Figure()

    # Calculate consistent badge size based on axis range
    xg_conv_range = df['XG_CONVERSION'].max() - df['XG_CONVERSION'].min()
    xga_conv_range = df['XGA_CONVERSION'].max() - df['XGA_CONVERSION'].min()
    badge_size_2 = min(xg_conv_range, xga_conv_range) * 0.08  # 8% of smallest axis range

    # Add scatter points with badges
    for idx, row in df.iterrows():
        team_name = row['TEAM']
        is_selected = (team_name == selected_team)

        badge_path = get_badge_path(team_name)

        # Determine marker style
        if is_selected:
            marker_size = 50
        else:
            marker_size = 35

        # Try to load badge image
        if badge_path:
            try:
                # Add badge as scatter marker using image with dynamic sizing
                fig2.add_layout_image(
                    dict(
                        source=Image.open(badge_path),
                        x=row['XG_CONVERSION'],
                        y=row['XGA_CONVERSION'],
                        xref="x",
                        yref="y",
                        sizex=badge_size_2,
                        sizey=badge_size_2,
                        xanchor="center",
                        yanchor="middle",
                        layer="above"
                    )
                )
            except:
                pass

        # Add invisible scatter point for hover
        fig2.add_trace(go.Scatter(
            x=[row['XG_CONVERSION']],
            y=[row['XGA_CONVERSION']],
            mode='markers',
            marker=dict(
                size=marker_size,
                color='rgba(0,0,0,0)',  # Transparent
                line=dict(width=0)
            ),
            hovertemplate=f'<b>{team_name}</b><br>xG Conv: {row["XG_CONVERSION"]:.3f}<br>xGA Conv: {row["XGA_CONVERSION"]:.3f}<extra></extra>',
            showlegend=False,
            name=team_name
        ))

    # Add y=x line (perfect balance line)
    # Teams above the line: opponents convert more chances
    # Teams below the line: team converts more chances
    min_conversion = min(df['XG_CONVERSION'].min(), df['XGA_CONVERSION'].min())
    max_conversion = max(df['XG_CONVERSION'].max(), df['XGA_CONVERSION'].max())
    fig2.add_trace(go.Scatter(
        x=[min_conversion, max_conversion],
        y=[min_conversion, max_conversion],
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dash'),
        showlegend=False,
        hoverinfo='skip',
        name='Balance Line (y=x)'
    ))

    fig2.update_layout(
        xaxis_title="xG Conversion",
        yaxis_title="xGA Conversion",
        height=450,
        hovermode='closest',
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#0e1117',
        font=dict(color='white', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        margin=dict(l=60, r=20, t=40, b=60)
    )

    st.plotly_chart(fig2, use_container_width=True)

with col2:
    # Team metrics header with better styling
    st.markdown(f"## 🏟️ {selected_team}")
    st.markdown("")

    # Key metrics in a more prominent display
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric(
            "xGD Per 90",
            f"{team_data['XGD_PER_90']:.2f}",
            delta=None
        )
    with metric_col2:
        st.metric(
            "Points/Game",
            f"{team_data['POINTS_PER_GAME']:.2f}",
            delta=None
        )

    st.markdown("---")

    # Attacking Values and Rank
    st.markdown("### ⚔️ Attacking Stats")

    attack_data = pd.DataFrame({
        'Metric': [
            'Goals',
            'xG',
            'Open Play xG',
            'Set Piece xG',
            'Set Piece Goals',
            'xG per 90',
            'xG Conversion'
        ],
        'Value': [
            f"{team_data['GOALS']:.0f}",
            f"{team_data['XG']:.2f}",
            f"{team_data['OPEN_PLAY_XG']:.2f}",
            f"{team_data['SET_PIECE_XG']:.2f}",
            f"{team_data['SET_PIECE_GOALS']:.0f}",
            f"{team_data['XG_PER_90']:.2f}",
            f"{team_data['XG_CONVERSION']:.3f}"
        ],
        'Rank': [
            team_data['goals_rank'],
            team_data['xg_rank'],
            team_data['open_play_xg_rank'],
            team_data['set_piece_xg_rank'],
            team_data['set_piece_goals_rank'],
            team_data['xg_per_90_rank'],
            team_data['xg_conversion_rank']
        ]
    })

    def color_rank_advanced(val, max_rank=24):
        """Enhanced color coding for ranks with better gradient"""
        try:
            rank = int(val)
            normalized = (rank - 1) / (max_rank - 1)

            # Better color gradient from green to red
            if normalized < 0.2:
                color = '#00C853'  # Bright green
                text_color = '#000000'
            elif normalized < 0.4:
                color = '#64DD17'  # Light green
                text_color = '#000000'
            elif normalized < 0.6:
                color = '#FFD600'  # Yellow
                text_color = '#000000'
            elif normalized < 0.8:
                color = '#FF6F00'  # Orange
                text_color = '#ffffff'
            else:
                color = '#D32F2F'  # Red
                text_color = '#ffffff'

            return f'background-color: {color}; color: {text_color}; font-weight: bold;'
        except:
            return ''

    styled_attack = attack_data.style.applymap(
        color_rank_advanced,
        subset=['Rank']
    ).set_properties(**{
        'text-align': 'left',
        'padding': '8px'
    }, subset=['Metric']).set_properties(**{
        'text-align': 'center',
        'padding': '8px'
    }, subset=['Value', 'Rank'])

    st.dataframe(styled_attack, use_container_width=True, hide_index=True, height=280)

    st.markdown("")

    # Defending Values and Rank
    st.markdown("### 🛡️ Defensive Stats")

    defend_data = pd.DataFrame({
        'Metric': [
            'Goals Against',
            'xG Against',
            'Open Play xGA',
            'Set Piece xGA',
            'Set Piece GA',
            'xGA per 90',
            'xGA Conversion'
        ],
        'Value': [
            f"{team_data['GOALS_AGAINST']:.0f}",
            f"{team_data['XGA']:.2f}",
            f"{team_data['OPEN_PLAY_XGA']:.2f}",
            f"{team_data['SET_PIECE_XGA']:.2f}",
            f"{team_data['SET_PIECE_GOALS_AGAINST']:.0f}",
            f"{team_data['XGA_PER_90']:.2f}",
            f"{team_data['XGA_CONVERSION']:.3f}"
        ],
        'Rank': [
            team_data['goals_against_rank'],
            team_data['xga_rank'],
            team_data['open_play_xga_rank'],
            team_data['set_piece_xga_rank'],
            team_data['set_piece_goals_against_rank'],
            team_data['xga_per_90_rank'],
            team_data['xga_conversion_rank']
        ]
    })

    styled_defend = defend_data.style.applymap(
        color_rank_advanced,
        subset=['Rank']
    ).set_properties(**{
        'text-align': 'left',
        'padding': '8px'
    }, subset=['Metric']).set_properties(**{
        'text-align': 'center',
        'padding': '8px'
    }, subset=['Value', 'Rank'])

    st.dataframe(styled_defend, use_container_width=True, hide_index=True, height=280)

with tab2:
    # Match-by-match trends for selected team
    st.markdown(f"## 📈 {selected_team} - Match Trends")

    # Load match data for selected team
    match_data = get_match_by_match_data(selected_team)

    if len(match_data) > 0:
        # Create two columns for the charts
        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:
            # Rolling 5-match xG vs xGA
            st.subheader("Rolling 5-Match xG Average")

            fig_rolling = go.Figure()

            # Use match_label (opponent name) on x-axis
            fig_rolling.add_trace(go.Scatter(
                x=match_data['match_label'],
                y=match_data['xg_rolling_5'],
                mode='lines+markers',
                name='xG (Rolling 5)',
                line=dict(color='#00C853', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>xG (Rolling 5): %{y:.2f}<extra></extra>'
            ))

            fig_rolling.add_trace(go.Scatter(
                x=match_data['match_label'],
                y=match_data['xga_rolling_5'],
                mode='lines+markers',
                name='xGA (Rolling 5)',
                line=dict(color='#FF4B4B', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>xGA (Rolling 5): %{y:.2f}<extra></extra>'
            ))

            fig_rolling.update_layout(
                xaxis_title="Match (Opponent)",
                yaxis_title="xG / xGA",
                height=400,
                hovermode='x unified',
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#0e1117',
                font=dict(color='white', size=12),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False,
                    tickangle=-45
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig_rolling, use_container_width=True)

        with trend_col2:
            # Points Progression Chart
            st.subheader("Points Progression vs 80 Point Target")

            # Calculate cumulative points and PPG
            match_data['cumulative_points'] = match_data['POINTS'].cumsum()
            match_data['ppg'] = match_data['cumulative_points'] / match_data['match_number']

            # Calculate expected points for each match using Poisson model
            match_data['xpoints'] = match_data.apply(
                lambda row: calculate_expected_points(row['XG_FOR'], row['XG_AGAINST']),
                axis=1
            )
            match_data['cumulative_xpoints'] = match_data['xpoints'].cumsum()
            match_data['xppg'] = match_data['cumulative_xpoints'] / match_data['match_number']

            # Calculate target PPG needed for 80 points in 46 games
            target_ppg = 80 / 46  # ~1.74 PPG

            fig_ppg = go.Figure()

            # Create x-axis from 1 to 46 matches
            x_matches = list(range(1, 47))

            # Get current PPG and xPPG, project across 46 matches
            current_ppg = match_data['ppg'].iloc[-1]
            current_xppg = match_data['xppg'].iloc[-1]
            y_current_projection = [current_ppg * x for x in x_matches]
            y_xpoints_projection = [current_xppg * x for x in x_matches]

            # Target line: 80 points pace
            y_target = [target_ppg * x for x in x_matches]

            # Team's projected points line (y = current_ppg * x)
            fig_ppg.add_trace(go.Scatter(
                x=x_matches,
                y=y_current_projection,
                mode='lines',
                name=f'Current Pace (PPG: {current_ppg:.2f})',
                line=dict(color='#4A90E2', width=3),
                hovertemplate='Match %{x}<br>Projected Points: %{y:.1f}<extra></extra>'
            ))

            # Expected points projection line (y = current_xppg * x)
            fig_ppg.add_trace(go.Scatter(
                x=x_matches,
                y=y_xpoints_projection,
                mode='lines',
                name=f'xPoints Pace (xPPG: {current_xppg:.2f})',
                line=dict(color='#FF6F00', width=3, dash='dot'),
                hovertemplate='Match %{x}<br>Projected xPoints: %{y:.1f}<extra></extra>'
            ))

            # Target line (y = 1.74 * x)
            fig_ppg.add_trace(go.Scatter(
                x=x_matches,
                y=y_target,
                mode='lines',
                name='80 Point Pace (PPG: 1.74)',
                line=dict(color='#00C853', width=3, dash='dash'),
                hovertemplate='Match %{x}<br>Target Points: %{y:.1f}<extra></extra>'
            ))

            fig_ppg.update_layout(
                xaxis_title="Match Number",
                yaxis_title="Points",
                height=400,
                hovermode='x unified',
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#0e1117',
                font=dict(color='white', size=12),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False,
                    range=[1, 46]
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False,
                    range=[0, 90]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig_ppg, use_container_width=True)

        # Match results table
        st.markdown("### Match Results")

        # Prepare display dataframe with rolling averages
        display_df = match_data[['match_number', 'OPPONENT', 'GOALS_FOR', 'GOALS_AGAINST', 'XG_FOR', 'XG_AGAINST', 'xg_rolling_5', 'xga_rolling_5', 'POINTS']].copy()
        display_df.columns = ['Match', 'Opponent', 'GF', 'GA', 'xG', 'xGA', 'xG (R5)', 'xGA (R5)', 'Pts']
        display_df['Result'] = display_df.apply(lambda row: 'W' if row['Pts'] == 3 else ('D' if row['Pts'] == 1 else 'L'), axis=1)
        display_df = display_df[['Match', 'Opponent', 'Result', 'GF', 'GA', 'xG', 'xGA', 'xG (R5)', 'xGA (R5)', 'Pts']]

        # Format numbers
        display_df['xG'] = display_df['xG'].round(2)
        display_df['xGA'] = display_df['xGA'].round(2)
        display_df['xG (R5)'] = display_df['xG (R5)'].round(2)
        display_df['xGA (R5)'] = display_df['xGA (R5)'].round(2)

        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No match data available for this team")

with tab3:
    # League Table with Expected Positions
    st.markdown("## 🏆 League Table: Actual vs Expected")
    st.markdown("Compare actual league positions with xG-based expected positions")
    st.markdown("")

    # Calculate expected points for all teams
    league_table = df.copy()

    # Calculate expected points using Poisson model
    def calculate_team_xpoints(team_name):
        """Calculate total expected points for a team across all matches"""
        match_data = get_match_by_match_data(team_name)
        if len(match_data) > 0:
            match_data['xpoints'] = match_data.apply(
                lambda row: calculate_expected_points(row['XG_FOR'], row['XG_AGAINST']),
                axis=1
            )
            return match_data['xpoints'].sum()
        return 0

    # Calculate xPoints for all teams
    with st.spinner('Calculating expected points for all teams...'):
        league_table['EXPECTED_POINTS'] = league_table['TEAM'].apply(calculate_team_xpoints)

    # Calculate goal difference for ranking
    league_table['GOAL_DIFF'] = league_table['GOALS'] - league_table['GOALS_AGAINST']
    league_table['XGD'] = league_table['XG'] - league_table['XGA']

    # Calculate positions using points then goal difference (standard football ranking)
    # Sort by points desc, then goal difference desc, then goals scored desc
    league_table = league_table.sort_values(
        by=['TOTAL_POINTS', 'GOAL_DIFF', 'GOALS'],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    league_table['ACTUAL_POSITION'] = range(1, len(league_table) + 1)

    # Sort by expected points, then xGD, then xG for expected position
    league_table_xg_sorted = league_table.sort_values(
        by=['EXPECTED_POINTS', 'XGD', 'XG'],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    league_table_xg_sorted['EXPECTED_POSITION'] = range(1, len(league_table_xg_sorted) + 1)

    # Merge expected position back
    league_table = league_table.merge(
        league_table_xg_sorted[['TEAM', 'EXPECTED_POSITION']],
        on='TEAM',
        how='left'
    )

    league_table['POSITION_DIFF'] = league_table['EXPECTED_POSITION'] - league_table['ACTUAL_POSITION']
    league_table['POINTS_DIFF'] = league_table['TOTAL_POINTS'] - league_table['EXPECTED_POINTS']

    # Get last 5 match form for each team
    def get_last_5_form(team_name):
        """Get form string for last 5 matches"""
        match_data = get_match_by_match_data(team_name)
        if len(match_data) >= 5:
            last_5 = match_data.tail(5)
            form = ''
            for _, row in last_5.iterrows():
                if row['POINTS'] == 3:
                    form += 'W'
                elif row['POINTS'] == 1:
                    form += 'D'
                else:
                    form += 'L'
            return form
        return 'N/A'

    with st.spinner('Loading form data...'):
        league_table['FORM'] = league_table['TEAM'].apply(get_last_5_form)

    # Prepare display dataframe
    display_table = league_table[[
        'ACTUAL_POSITION', 'TEAM', 'MATCHES_PLAYED', 'TOTAL_POINTS',
        'EXPECTED_POINTS', 'POINTS_DIFF', 'EXPECTED_POSITION', 'POSITION_DIFF',
        'GOALS', 'GOALS_AGAINST', 'XG', 'XGA', 'FORM'
    ]].copy()

    display_table.columns = [
        'Pos', 'Team', 'P', 'Pts', 'xPts', 'Pts Diff', 'xPos', 'Pos Diff',
        'GF', 'GA', 'xGF', 'xGA', 'Form'
    ]

    # Format numbers - remove trailing zeros
    display_table['xPts'] = display_table['xPts'].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))
    display_table['Pts Diff'] = display_table['Pts Diff'].apply(lambda x: f"{x:+.2f}".rstrip('0').rstrip('.'))
    display_table['Pos Diff'] = display_table['Pos Diff'].apply(lambda x: f"{x:+d}" if x != 0 else "–")
    display_table['xGF'] = display_table['xGF'].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))
    display_table['xGA'] = display_table['xGA'].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    # Style function for the table
    def style_league_table(df):
        """Apply styling to league table"""
        def color_position_diff(val):
            """Color code position difference"""
            try:
                if val == "–":
                    return 'background-color: #333333; color: white;'
                num = int(val)
                if num > 0:  # Underperforming (expected position worse)
                    return 'background-color: #D32F2F; color: white; font-weight: bold;'
                elif num < 0:  # Overperforming (expected position better)
                    return 'background-color: #00C853; color: black; font-weight: bold;'
                else:
                    return 'background-color: #333333; color: white;'
            except:
                return ''

        def color_points_diff(val):
            """Color code points difference"""
            try:
                num = float(val)
                if num > 2:
                    return 'background-color: #00C853; color: black; font-weight: bold;'
                elif num > 0:
                    return 'background-color: #64DD17; color: black; font-weight: bold;'
                elif num < -2:
                    return 'background-color: #D32F2F; color: white; font-weight: bold;'
                elif num < 0:
                    return 'background-color: #FF6F00; color: white; font-weight: bold;'
                else:
                    return 'background-color: #333333; color: white;'
            except:
                return ''

        def highlight_selected_team(row):
            """Highlight the selected team"""
            if row['Team'] == selected_team:
                return ['background-color: #4A90E2; color: white; font-weight: bold;'] * len(row)
            return [''] * len(row)

        styled = df.style.apply(highlight_selected_team, axis=1)
        styled = styled.applymap(color_position_diff, subset=['Pos Diff'])
        styled = styled.applymap(color_points_diff, subset=['Pts Diff'])

        return styled.set_properties(**{
            'text-align': 'center',
            'padding': '8px'
        }).set_properties(**{
            'text-align': 'left',
            'padding': '8px'
        }, subset=['Team'])

    st.dataframe(
        style_league_table(display_table),
        use_container_width=True,
        hide_index=True,
        height=600
    )

    # Add explanation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Points Difference**")
        st.markdown("- 🟢 **Positive**: Overperforming xG (lucky)")
        st.markdown("- 🔴 **Negative**: Underperforming xG (unlucky)")

    with col2:
        st.markdown("**📍 Position Difference**")
        st.markdown("- 🟢 **Negative**: Better position than xG suggests")
        st.markdown("- 🔴 **Positive**: Worse position than xG suggests")

    with col3:
        st.markdown("**📈 Form (Last 5)**")
        st.markdown("- **W** = Win, **D** = Draw, **L** = Loss")
        st.markdown("- Most recent match on the right")

with tab4:
    # Team Comparison Tool
    st.markdown("## ⚖️ Head-to-Head Team Comparison")
    st.markdown("Select 2-3 teams to compare their stats side-by-side")
    st.markdown("")

    # Team selection
    col1, col2, col3 = st.columns(3)

    with col1:
        compare_team_1 = st.selectbox(
            "Team 1",
            options=sorted(df['TEAM'].unique()),
            index=sorted(df['TEAM'].unique()).index(selected_team) if selected_team in df['TEAM'].unique() else 0,
            key='compare_1'
        )

    with col2:
        compare_team_2 = st.selectbox(
            "Team 2",
            options=sorted(df['TEAM'].unique()),
            index=1,
            key='compare_2'
        )

    with col3:
        compare_team_3 = st.selectbox(
            "Team 3 (Optional)",
            options=['None'] + sorted(df['TEAM'].unique()),
            index=0,
            key='compare_3'
        )

    # Get data for selected teams
    comparison_teams = [compare_team_1, compare_team_2]
    if compare_team_3 != 'None':
        comparison_teams.append(compare_team_3)

    comparison_data = df[df['TEAM'].isin(comparison_teams)].copy()

    st.markdown("---")

    # Performance Comparison Chart - Individual Pizza Charts
    st.subheader("📊 Overall Performance Comparison")

    # Prepare comparison data
    categories = ['xG/90', 'xGA/90 (inv)', 'xG Conv.', 'xGA Conv. (inv)', 'PPG', 'xGD/90']

    colors = ['#4A90E2', '#FF6F00', '#00C853']

    # Calculate percentile rankings for all teams (0-100 scale)
    # Higher percentile = better performance
    df['xg90_percentile'] = df['XG_PER_90'].rank(pct=True) * 100
    df['xga90_percentile'] = (1 - df['XGA_PER_90'].rank(pct=True)) * 100  # Inverted - lower is better
    df['xg_conv_percentile'] = df['XG_CONVERSION'].rank(pct=True) * 100
    df['xga_conv_percentile'] = (1 - df['XGA_CONVERSION'].rank(pct=True)) * 100  # Inverted - lower is better
    df['ppg_percentile'] = df['POINTS_PER_GAME'].rank(pct=True) * 100
    df['xgd90_percentile'] = df['XGD_PER_90'].rank(pct=True) * 100

    # Create columns for side-by-side pizza charts
    chart_cols = st.columns(len(comparison_teams))

    for idx, team in enumerate(comparison_teams):
        with chart_cols[idx]:
            team_data = df[df['TEAM'] == team].iloc[0]

            # Get percentile values (0-100 scale)
            percentile_values = [
                team_data['xg90_percentile'],
                team_data['xga90_percentile'],
                team_data['xg_conv_percentile'],
                team_data['xga_conv_percentile'],
                team_data['ppg_percentile'],
                team_data['xgd90_percentile']
            ]

            # Get actual values for hover
            actual_values = [
                team_data['XG_PER_90'],
                team_data['XGA_PER_90'],
                team_data['XG_CONVERSION'],
                team_data['XGA_CONVERSION'],
                team_data['POINTS_PER_GAME'],
                team_data['XGD_PER_90']
            ]

            # Create labels with percentile
            percentile_labels = [f"{p:.0f}th" for p in percentile_values]

            # Create individual polar area chart (pizza chart)
            fig_pizza = go.Figure()

            fig_pizza.add_trace(go.Barpolar(
                r=percentile_values,
                theta=categories,
                name=team,
                marker=dict(
                    color=colors[idx],
                    line=dict(color='white', width=2)
                ),
                opacity=0.8,
                text=percentile_labels,
                hovertemplate='<b>%{theta}</b><br>Percentile: %{text}<br>Actual Value: %{customdata:.2f}<extra></extra>',
                customdata=actual_values
            ))

            fig_pizza.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=False,  # Hide radial axis
                        range=[0, 100]
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255, 255, 255, 0.2)',
                        linecolor='rgba(255, 255, 255, 0.3)',
                        tickfont=dict(size=11, color='white')
                    ),
                    bgcolor='#1a1a1a'
                ),
                showlegend=False,
                height=450,
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#0e1117',
                font=dict(color='white', size=10),
                title=dict(
                    text=f"<b>{team}</b>",
                    font=dict(size=15, color=colors[idx]),
                    x=0.5,
                    xanchor='center'
                ),
                margin=dict(l=70, r=70, t=70, b=70)
            )

            st.plotly_chart(fig_pizza, use_container_width=True)

    st.markdown("---")

    # Side-by-side comparison table
    st.subheader("📋 Detailed Comparison")

    # Create comparison table
    metrics = {
        'Points per Game': 'POINTS_PER_GAME',
        'Total Points': 'TOTAL_POINTS',
        'xGD per 90': 'XGD_PER_90',
        'xG per 90': 'XG_PER_90',
        'xGA per 90': 'XGA_PER_90',
        'Goals': 'GOALS',
        'Goals Against': 'GOALS_AGAINST',
        'xG': 'XG',
        'xGA': 'XGA',
        'xG Conversion': 'XG_CONVERSION',
        'xGA Conversion': 'XGA_CONVERSION',
        'Open Play xG': 'OPEN_PLAY_XG',
        'Set Piece xG': 'SET_PIECE_XG',
    }

    comparison_table = pd.DataFrame({'Metric': list(metrics.keys())})

    for team in comparison_teams:
        team_data = comparison_data[comparison_data['TEAM'] == team].iloc[0]
        values = []
        for metric_col in metrics.values():
            val = team_data[metric_col]
            if isinstance(val, float):
                values.append(f"{val:.2f}")
            else:
                values.append(str(val))
        comparison_table[team] = values

    st.dataframe(comparison_table, use_container_width=True, hide_index=True, height=500)

    st.markdown("---")

    # Recent form streak visualization
    st.subheader("📈 Recent Form (Last 10 Matches)")
    st.markdown("🟢 = Win | 🟡 = Draw | 🔴 = Loss | Hover for details")
    st.markdown("")

    for idx, team in enumerate(comparison_teams):
        match_data = get_match_by_match_data(team)

        if len(match_data) > 0:
            last_10 = match_data.tail(10)

            # Create form streak visualization
            st.markdown(f"### {team}")

            # Calculate stats
            total_points = last_10['POINTS'].sum()
            avg_xg = last_10['XG_FOR'].mean()
            avg_xga = last_10['XG_AGAINST'].mean()
            wins = (last_10['POINTS'] == 3).sum()
            draws = (last_10['POINTS'] == 1).sum()
            losses = (last_10['POINTS'] == 0).sum()

            # Show summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Points", f"{total_points}")
            with col2:
                st.metric("Record", f"{wins}W-{draws}D-{losses}L")
            with col3:
                st.metric("Avg xG", f"{avg_xg:.2f}")
            with col4:
                st.metric("Avg xGA", f"{avg_xga:.2f}")

            # Create form boxes with plotly
            fig_form = go.Figure()

            # Create boxes for each match
            box_width = 0.8
            for i, (_, match) in enumerate(last_10.iterrows()):
                # Determine result and color
                if match['POINTS'] == 3:
                    color = '#00C853'  # Green for win
                    result = 'W'
                elif match['POINTS'] == 1:
                    color = '#FFD600'  # Yellow for draw
                    result = 'D'
                else:
                    color = '#D32F2F'  # Red for loss
                    result = 'L'

                # Calculate xG difference
                xgd = match['XG_FOR'] - match['XG_AGAINST']

                # Add rectangle for match result
                fig_form.add_trace(go.Bar(
                    x=[i],
                    y=[1],
                    width=box_width,
                    marker=dict(
                        color=color,
                        line=dict(color='white', width=2)
                    ),
                    name=result,
                    showlegend=False,
                    text=result,
                    textposition='inside',
                    textfont=dict(size=18, color='white', family='Arial Black'),
                    hovertemplate=(
                        f"<b>vs {match['OPPONENT']}</b><br>"
                        f"Result: {result} ({match['GOALS_FOR']}-{match['GOALS_AGAINST']})<br>"
                        f"xG: {match['XG_FOR']:.2f} - {match['XG_AGAINST']:.2f}<br>"
                        f"xGD: {xgd:+.2f}<br>"
                        f"Points: {match['POINTS']}<extra></extra>"
                    )
                ))

            fig_form.update_layout(
                height=120,
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#0e1117',
                xaxis=dict(
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    range=[-0.5, 9.5]
                ),
                yaxis=dict(
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    range=[0, 1.1]
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                bargap=0.1
            )

            st.plotly_chart(fig_form, use_container_width=True)

        st.markdown("")

# Footer
st.markdown("---")
st.markdown(
    '<p class="caption">📊 Data updates weekly from Snowflake • Championship 25/26 Season</p>',
    unsafe_allow_html=True
)
