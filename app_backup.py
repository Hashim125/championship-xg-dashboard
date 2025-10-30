import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from database import get_team_stats, get_match_by_match_data
from badge_mapping import get_badge_path
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Championship xG Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Main layout - 65/35 split for better visualization space
col1, col2 = st.columns([1.85, 1])

with col1:
    # Scatter Plot 1: xG Per 90 vs xGA Per 90
    st.subheader("📈 xG Per 90 vs xGA Per 90")

    fig1 = go.Figure()

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
                # Add badge as scatter marker using image
                fig1.add_layout_image(
                    dict(
                        source=Image.open(badge_path),
                        x=row['XG_PER_90'],
                        y=row['XGA_PER_90'],
                        xref="x",
                        yref="y",
                        sizex=0.12 if is_selected else 0.09,
                        sizey=0.12 if is_selected else 0.09,
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

    # Add trend line through origin (y = mx, where x is xG and y is xGA)
    # Line with slope = 1 means xGA = xG (perfect balance)
    max_val = max(df['XG_PER_90'].max(), df['XGA_PER_90'].max())
    fig1.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dash'),
        showlegend=False,
        hoverinfo='skip',
        name='Balance Line'
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
                # Add badge as scatter marker using image
                fig2.add_layout_image(
                    dict(
                        source=Image.open(badge_path),
                        x=row['XG_CONVERSION'],
                        y=row['XGA_CONVERSION'],
                        xref="x",
                        yref="y",
                        sizex=0.08 if is_selected else 0.06,
                        sizey=0.08 if is_selected else 0.06,
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

    # Add trend line through origin (1:1 balance line)
    max_conversion = max(df['XG_CONVERSION'].max(), df['XGA_CONVERSION'].max())
    fig2.add_trace(go.Scatter(
        x=[0, max_conversion],
        y=[0, max_conversion],
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dash'),
        showlegend=False,
        hoverinfo='skip',
        name='Balance Line'
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

# Footer
st.markdown("---")
st.markdown(
    '<p class="caption">📊 Data updates weekly from Snowflake • Championship 25/26 Season</p>',
    unsafe_allow_html=True
)
