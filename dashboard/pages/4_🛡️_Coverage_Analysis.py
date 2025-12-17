"""
🛡️ Coverage Analysis
Compare RAI performance across coverage schemes
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.themes import apply_theme, COLORS, get_plotly_layout
from components.data_loader import (
    load_rai_results,
    get_coverage_analysis,
)

apply_theme()

st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 2rem; font-weight: 700; margin: 0;">🛡️ Coverage Analysis</h1>
    <p style="color: #9CA3AF; margin: 8px 0 0 0;">RAI performance by coverage type and scheme</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading coverage data..."):
    coverage_df = get_coverage_analysis()

if coverage_df is not None and not coverage_df.empty:
    # Check for coverage columns
    has_coverage_type = 'pff_passCoverageType' in coverage_df.columns
    has_coverage = 'pff_passCoverage' in coverage_df.columns
    
    if has_coverage_type or has_coverage:
        st.markdown("### 📊 RAI by Coverage Type")
        
        layout = get_plotly_layout()
        
        # Coverage type analysis
        if has_coverage_type:
            coverage_type_col = 'pff_passCoverageType'
        elif has_coverage:
            coverage_type_col = 'pff_passCoverage'
        else:
            coverage_type_col = None
        
        if coverage_type_col:
            # Clean coverage column
            coverage_df[coverage_type_col] = coverage_df[coverage_type_col].fillna('Unknown')
            
            # Aggregate by coverage type
            coverage_agg = coverage_df.groupby(coverage_type_col).agg({
                'rai': ['mean', 'std', 'count'],
            }).reset_index()
            coverage_agg.columns = ['Coverage Type', 'Avg RAI', 'Std RAI', 'Play Count']
            coverage_agg = coverage_agg[coverage_agg['Play Count'] >= 10]  # Filter low counts
            coverage_agg = coverage_agg.sort_values('Avg RAI', ascending=False)
            
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                # Bar chart
                fig_coverage = go.Figure()
                
                fig_coverage.add_trace(go.Bar(
                    x=coverage_agg['Coverage Type'],
                    y=coverage_agg['Avg RAI'],
                    marker=dict(
                        color=coverage_agg['Avg RAI'],
                        colorscale=[
                            [0, COLORS['error']],
                            [0.5, COLORS['warning']],
                            [1, COLORS['success']],
                        ],
                    ),
                    text=[f"{x:.3f}" for x in coverage_agg['Avg RAI']],
                    textposition='outside',
                    error_y=dict(
                        type='data',
                        array=coverage_agg['Std RAI'],
                        visible=True,
                        color=COLORS['text_muted'],
                    ),
                ))
                
                fig_coverage.update_layout(
                    **layout,
                    title="Average RAI by Coverage Scheme",
                    xaxis_title="Coverage Type",
                    yaxis_title="Average RAI",
                    height=450,
                    showlegend=False,
                )
                
                st.plotly_chart(fig_coverage, use_container_width=True)
            
            with col2:
                st.markdown("#### Coverage Breakdown")
                
                for _, row in coverage_agg.head(8).iterrows():
                    pct = row['Play Count'] / coverage_agg['Play Count'].sum() * 100
                    rai_color = COLORS['success'] if row['Avg RAI'] > 0.5 else (
                        COLORS['warning'] if row['Avg RAI'] > 0 else COLORS['error']
                    )
                    
                    st.markdown(f"""
                    <div style="background: rgba(28, 37, 65, 0.7); padding: 12px; 
                                border-radius: 8px; margin: 8px 0; border-left: 3px solid {rai_color};">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 500;">{row['Coverage Type']}</span>
                            <span style="color: {rai_color};">RAI: {row['Avg RAI']:.3f}</span>
                        </div>
                        <div style="color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;">
                            {int(row['Play Count']):,} plays ({pct:.1f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Man vs Zone comparison
        st.markdown("### 🆚 Man vs Zone Coverage")
        
        # Categorize coverage types
        coverage_df['coverage_category'] = coverage_df[coverage_type_col].apply(
            lambda x: 'Man' if 'MAN' in str(x).upper() else (
                'Zone' if 'ZONE' in str(x).upper() else 'Other'
            )
        )
        
        man_zone_agg = coverage_df.groupby('coverage_category').agg({
            'rai': ['mean', 'std', 'count'],
            'rtd': 'mean',
            'te': 'mean',
        }).reset_index()
        man_zone_agg.columns = ['Category', 'Avg RAI', 'Std RAI', 'Plays', 'Avg RTD', 'Avg TE']
        
        mz_cols = st.columns(3)
        for i, cat in enumerate(['Man', 'Zone', 'Other']):
            cat_data = man_zone_agg[man_zone_agg['Category'] == cat]
            if not cat_data.empty:
                with mz_cols[i]:
                    cat_row = cat_data.iloc[0]
                    icon = "🎯" if cat == 'Man' else ("🔲" if cat == 'Zone' else "❓")
                    color = COLORS['receiver'] if cat == 'Man' else (
                        COLORS['defender'] if cat == 'Zone' else COLORS['neutral']
                    )
                    
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center; border-top: 3px solid {color};">
                        <div style="font-size: 2.5rem;">{icon}</div>
                        <h3 style="color: {color}; margin: 8px 0;">{cat} Coverage</h3>
                        <div class="metric-value">{cat_row['Avg RAI']:.3f}</div>
                        <div style="color: #9CA3AF; font-size: 0.875rem;">Avg RAI</div>
                        <div style="margin-top: 16px; display: flex; justify-content: space-around;">
                            <div>
                                <div style="color: #9CA3AF; font-size: 0.75rem;">RTD</div>
                                <div>{cat_row['Avg RTD']:.1f}</div>
                            </div>
                            <div>
                                <div style="color: #9CA3AF; font-size: 0.75rem;">TE</div>
                                <div>{cat_row['Avg TE']:.1%}</div>
                            </div>
                            <div>
                                <div style="color: #9CA3AF; font-size: 0.75rem;">Plays</div>
                                <div>{int(cat_row['Plays']):,}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Receiver vs Defender by coverage
        st.markdown("### 📊 RAI by Role and Coverage")
        
        role_coverage = coverage_df.groupby(['coverage_category', 'player_role']).agg({
            'rai': 'mean',
        }).reset_index()
        
        fig_heatmap = px.density_heatmap(
            coverage_df,
            x='coverage_category',
            y='player_role',
            z='rai',
            histfunc='avg',
            color_continuous_scale=[
                [0, COLORS['error']],
                [0.5, COLORS['neutral']],
                [1, COLORS['primary']],
            ],
        )
        
        fig_heatmap.update_layout(
            **layout,
            title="",
            xaxis_title="Coverage Category",
            yaxis_title="Player Role",
            height=350,
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Distribution by coverage
        st.markdown("### 📈 RAI Distribution by Coverage")
        
        fig_box = px.box(
            coverage_df[coverage_df['coverage_category'].isin(['Man', 'Zone'])],
            x='coverage_category',
            y='rai',
            color='player_role',
            color_discrete_map={
                'Targeted Receiver': COLORS['receiver'],
                'Defensive Coverage': COLORS['defender'],
            },
        )
        
        fig_box.update_layout(
            **layout,
            title="",
            xaxis_title="Coverage Type",
            yaxis_title="RAI Score",
            height=400,
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    else:
        st.info("Coverage type information not available in the dataset.")
        st.markdown("""
        To enable coverage analysis, ensure your supplementary data includes:
        - `pff_passCoverageType` (e.g., COVER_1_MAN, COVER_2_ZONE)
        - `pff_passCoverage` (e.g., MAN_COVERAGE, ZONE_COVERAGE)
        """)
        
        # Show basic distribution instead
        st.markdown("### 📊 RAI Distribution by Role")
        
        fig = px.violin(
            coverage_df,
            x='player_role',
            y='rai',
            color='player_role',
            color_discrete_map={
                'Targeted Receiver': COLORS['receiver'],
                'Defensive Coverage': COLORS['defender'],
            },
            box=True,
        )
        
        layout = get_plotly_layout()
        fig.update_layout(**layout, height=450)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data available for coverage analysis.")
