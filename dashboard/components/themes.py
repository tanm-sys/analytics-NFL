"""
NFL RAI Dashboard - Theme Configuration
NFL-inspired colors with dark/light mode support
"""

# NFL-inspired color palette
COLORS = {
    'primary': '#FFB81C',      # NFL Gold
    'secondary': '#0B132B',    # Deep Navy
    'background': '#0B132B',   # Dark background
    'surface': '#1C2541',      # Card surface
    'accent': '#3A506B',       # Muted accent
    'text': '#FAFAFA',         # Light text
    'text_muted': '#9CA3AF',   # Muted text
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'error': '#EF4444',        # Red
    'receiver': '#3B82F6',     # Blue for receivers
    'defender': '#EF4444',     # Red for defenders
    'neutral': '#6B7280',      # Gray
}

# Plotly dark template configuration
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': COLORS['text'], 'family': 'Inter, sans-serif'},
        'xaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)',
        },
        'yaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)',
        },
        'colorway': [
            COLORS['primary'], COLORS['receiver'], COLORS['defender'],
            COLORS['success'], '#8B5CF6', '#EC4899', '#06B6D4'
        ],
    }
}

# CSS for glassmorphism and animations
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(28, 37, 65, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        margin: 8px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric cards */
    .metric-container {
        background: linear-gradient(135deg, #1C2541 0%, #0B132B 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 184, 28, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FFB81C, #FF6B6B, #4ECDC4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFB81C;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B132B 0%, #1C2541 100%);
    }
    
    /* Hide default metrics delta arrow colors */
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFB81C 0%, #FF8C00 100%);
        color: #0B132B;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(255, 184, 28, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(28, 37, 65, 0.5);
        border-radius: 12px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0B132B;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3A506B;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FFB81C;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #FFB81C !important;
    }
</style>
"""

def apply_theme():
    """Apply custom theme CSS."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def get_plotly_layout():
    """Get Plotly layout with theme applied."""
    return PLOTLY_TEMPLATE['layout'].copy()
