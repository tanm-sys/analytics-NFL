"""
🏈 NFL RAI Interactive Dashboard
World-class analytics platform for Reactivity Advantage Index
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="NFL RAI Dashboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/nfl-big-data-bowl',
        'Report a bug': None,
        'About': """
        ## NFL Reactivity Advantage Index Dashboard
        
        A world-class interactive analytics platform for analyzing 
        player reaction quality during the ball-in-air window.
        
        **Built with:**
        - Streamlit 1.41+
        - Plotly 5.24+
        - Python 3.11+
        """
    }
)

# Import components after page config
from components.themes import apply_theme, COLORS
from components.data_loader import get_summary_stats, load_rai_results

# Apply custom theme
apply_theme()

# Session state initialization
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None


def main():
    """Main dashboard entry point."""
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; margin: 0;">🏈</h1>
            <h2 style="margin: 10px 0; font-weight: 700; background: linear-gradient(135deg, #FFB81C 0%, #FF6B6B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                NFL RAI
            </h2>
            <p style="color: #9CA3AF; font-size: 0.875rem; margin: 0;">
                Reactivity Advantage Index
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation hint
        st.markdown("""
        <div style="padding: 16px; background: rgba(255, 184, 28, 0.1); border-radius: 8px; border-left: 3px solid #FFB81C;">
            <p style="margin: 0; font-size: 0.875rem; color: #FFB81C;">
                📍 <strong>Navigation</strong>
            </p>
            <p style="margin: 8px 0 0 0; font-size: 0.8rem; color: #9CA3AF;">
                Use the pages in the sidebar to explore different analytics views.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick stats
        try:
            stats = get_summary_stats()
            st.markdown("### 📊 Quick Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Players", f"{stats.get('total_players', 0):,}")
            with col2:
                st.metric("Plays", f"{stats.get('total_plays', 0):,}")
            
            st.metric("Avg RAI", f"{stats.get('avg_rai', 0):.3f}")
            
        except Exception as e:
            st.warning("Data loading in progress...")
        
        st.divider()
        
        # Theme toggle
        st.markdown("### ⚙️ Settings")
        theme_options = st.selectbox(
            "Theme",
            ["Dark (NFL)", "Light"],
            index=0 if st.session_state.theme == 'dark' else 1,
            key='theme_selector'
        )
        st.session_state.theme = 'dark' if 'Dark' in theme_options else 'light'
        
        # Footer
        st.markdown("""
        ---
        <div style="text-align: center; padding: 10px 0; color: #6B7280; font-size: 0.75rem;">
            <p>NFL Big Data Bowl 2026</p>
            <p>© 2024 RAI Analytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area - Landing page
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 3.5rem; font-weight: 700; margin-bottom: 16px; background: linear-gradient(135deg, #FFB81C 0%, #FF6B6B 50%, #4ECDC4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            NFL Reactivity Advantage Index
        </h1>
        <p style="font-size: 1.25rem; color: #9CA3AF; max-width: 600px; margin: 0 auto 40px;">
            Analyzing cognitive and physical reaction quality during the critical ball-in-air window
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card animate-fade-in" style="animation-delay: 0.1s;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">📊</div>
            <h3 style="color: #FFB81C; margin-bottom: 8px;">Overview</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">
                KPI dashboards, 3D visualizations, and distribution analysis of RAI metrics across all players.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card animate-fade-in" style="animation-delay: 0.2s;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">🏃</div>
            <h3 style="color: #FFB81C; margin-bottom: 8px;">Player Explorer</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">
                Deep-dive into individual players with radar charts, component breakdowns, and comparisons.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card animate-fade-in" style="animation-delay: 0.3s;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">🏈</div>
            <h3 style="color: #FFB81C; margin-bottom: 8px;">Play Analysis</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">
                3D interactive field visualization with player trajectories and ball flight paths.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("""
        <div class="glass-card animate-fade-in" style="animation-delay: 0.4s;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">🛡️</div>
            <h3 style="color: #FFB81C; margin-bottom: 8px;">Coverage Analysis</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">
                Compare RAI performance across different coverage schemes and defensive alignments.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="glass-card animate-fade-in" style="animation-delay: 0.5s;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">🏆</div>
            <h3 style="color: #FFB81C; margin-bottom: 8px;">Leaderboards</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">
                Top performers, team rankings, and exportable data tables with advanced filtering.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin-top: 60px;">
        <p style="color: #6B7280; font-size: 1rem;">
            👈 Select a page from the sidebar to get started
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # RAI Components explanation
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with st.expander("📖 Understanding RAI Components", expanded=False):
        st.markdown("""
        ### Reactivity Advantage Index (RAI) Components
        
        The RAI metric captures player reaction quality during the **ball-in-air window** 
        (from pass release to catch/incompletion). It consists of five key components:
        
        | Component | Description | Best Score |
        |-----------|-------------|------------|
        | **RTD** (Reaction Time Delay) | Frames until significant movement change after ball release | Lower is better |
        | **TE** (Trajectory Efficiency) | Direct path vs actual path traveled | Higher is better (max 1.0) |
        | **BPQ** (Break Point Quality) | Sharpness of route breaks for receivers | Higher is better (max 1.0) |
        | **CMS** (Coverage Maintenance Score) | Defender tracking of ball trajectory | Higher is better (max 1.0) |
        | **SD** (Separation Delta) | Change in receiver-defender distance | Positive = receiver advantage |
        
        ---
        
        **Composite RAI Score:**
        - Role-weighted combination of normalized components
        - Receivers: Emphasis on BPQ and TE
        - Defenders: Emphasis on CMS and RTD
        """)


if __name__ == "__main__":
    main()
