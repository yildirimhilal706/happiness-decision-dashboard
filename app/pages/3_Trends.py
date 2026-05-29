"""
Trends Page
Year-over-year analysis: global trends, regional comparison, biggest movers
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import load_happiness_data
from utils.profiles import KDS_METRICS
from utils.flags import get_flag_url


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Trends — Happiness Dashboard",
    page_icon="📈",
    layout="wide",
)


# === CSS ===
st.markdown("""
<style>
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #C8553D 0%, #E8A87C 50%, #7A8450 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        line-height: 1.1;
    }
    .insight-card {
        background: #F4E3C2;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #C8553D;
        margin: 0.8rem 0;
    }
    .mover-card {
        background: #F4E3C2;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        height: 100%;
    }
    .divider {
        margin: 2.5rem 0 1.5rem 0;
        border-top: 1px dashed #C8B79D;
    }
    [data-testid="stMetricValue"] { font-size: 1.4rem; color: #2D2A26; }
    [data-testid="stMetricLabel"] { color: #5C5650; }
</style>
""", unsafe_allow_html=True)


# === LOAD ===
df = load_happiness_data()
years = sorted(df['Year'].unique())
first_year = years[0]
last_year = years[-1]


# === HERO ===
st.markdown('<div class="hero-title">Trends Over Time</div>', unsafe_allow_html=True)
st.caption(
    f"How did happiness shift between {first_year} and {last_year}? "
    "Global trajectories, regional patterns, and the biggest movers."
)


# === SECTION 1: GLOBAL TREND ===
st.markdown("### 🌍 The Global Trajectory")

global_avg = df.groupby('Year').agg(
    mean_score=('Happiness score', 'mean'),
    median_score=('Happiness score', 'median'),
    country_count=('Country', 'nunique'),
).reset_index()

col1, col2 = st.columns([2, 1])

with col1:
    fig_global = go.Figure()

    # Mean line
    fig_global.add_trace(go.Scatter(
        x=global_avg['Year'],
        y=global_avg['mean_score'],
        mode='lines+markers',
        name='Global Mean',
        line=dict(color='#C8553D', width=3),
        marker=dict(size=10, color='#C8553D'),
        hovertemplate='<b>%{x}</b><br>Mean: %{y:.3f}<extra></extra>',
    ))

    # Median (dashed)
    fig_global.add_trace(go.Scatter(
        x=global_avg['Year'],
        y=global_avg['median_score'],
        mode='lines+markers',
        name='Global Median',
        line=dict(color='#7A8450', width=2, dash='dash'),
        marker=dict(size=8, color='#7A8450'),
        hovertemplate='<b>%{x}</b><br>Median: %{y:.3f}<extra></extra>',
    ))

    fig_global.update_layout(
        height=400,
        plot_bgcolor='#FAF3E0',
        paper_bgcolor='#FAF3E0',
        xaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Year'),
        yaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Happiness Score'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_global, use_container_width=True)

with col2:
    first_mean = global_avg.iloc[0]['mean_score']
    last_mean = global_avg.iloc[-1]['mean_score']
    delta = last_mean - first_mean

    st.metric(
        f"Global mean {first_year}",
        f"{first_mean:.3f}",
    )
    st.metric(
        f"Global mean {last_year}",
        f"{last_mean:.3f}",
        delta=f"{delta:+.3f}",
    )
    st.metric(
        "Countries reported",
        f"{int(global_avg.iloc[-1]['country_count'])} / {int(global_avg.iloc[0]['country_count'])}",
        delta=f"{int(global_avg.iloc[-1]['country_count']) - int(global_avg.iloc[0]['country_count']):+d}",
        delta_color="normal" if global_avg.iloc[-1]['country_count'] >= global_avg.iloc[0]['country_count'] else "inverse",
    )


# === SECTION 2: REGIONAL COMPARISON ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🗺️ Regional Trajectories")
st.caption("How each world region's happiness has evolved.")

regional = df.groupby(['Year', 'Regional indicator']).agg(
    mean_score=('Happiness score', 'mean'),
).reset_index()

# Pretty color palette in earth tones
REGION_COLORS = {
    'Western Europe': '#7A8450',
    'North America and ANZ': '#C8553D',
    'Latin America and Caribbean': '#E8A87C',
    'Central and Eastern Europe': '#A14A2A',
    'East Asia': '#A8C09A',
    'Southeast Asia': '#D4A574',
    'South Asia': '#B07A4C',
    'Middle East and North Africa': '#9B5D3C',
    'Sub-Saharan Africa': '#6B4423',
    'Commonwealth of Independent States': '#5C7048',
}

fig_regional = go.Figure()

for region in regional['Regional indicator'].dropna().unique():
    region_data = regional[regional['Regional indicator'] == region]
    color = REGION_COLORS.get(region, '#7A8450')
    fig_regional.add_trace(go.Scatter(
        x=region_data['Year'],
        y=region_data['mean_score'],
        mode='lines+markers',
        name=region,
        line=dict(color=color, width=2),
        marker=dict(size=6, color=color),
        hovertemplate=f'<b>{region}</b><br>%{{x}}: %{{y:.2f}}<extra></extra>',
    ))

fig_regional.update_layout(
    height=480,
    plot_bgcolor='#FAF3E0',
    paper_bgcolor='#FAF3E0',
    xaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Year'),
    yaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Average Happiness Score'),
    legend=dict(orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.02, font=dict(size=10)),
    margin=dict(l=20, r=20, t=20, b=20),
)
st.plotly_chart(fig_regional, use_container_width=True)


# === SECTION 3: BIGGEST MOVERS ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"### 🚀 Biggest Movers ({first_year} → {last_year})")
st.caption(
    "Countries with the largest happiness score change. "
    "Only countries with data in both years are included."
)

# Build country-level changes
first_year_data = df[df['Year'] == first_year][['Country', 'Happiness score', 'Ranking']].rename(
    columns={'Happiness score': 'score_start', 'Ranking': 'rank_start'}
)
last_year_data = df[df['Year'] == last_year][['Country', 'Happiness score', 'Ranking']].rename(
    columns={'Happiness score': 'score_end', 'Ranking': 'rank_end'}
)
movers = first_year_data.merge(last_year_data, on='Country', how='inner')
movers['score_change'] = movers['score_end'] - movers['score_start']
movers['rank_change'] = movers['rank_start'] - movers['rank_end']  # positive = improved

# Top 5 risers and 5 fallers
risers = movers.nlargest(5, 'score_change').reset_index(drop=True)
fallers = movers.nsmallest(5, 'score_change').reset_index(drop=True)

col_r, col_f = st.columns(2)

with col_r:
    st.markdown("#### 🟢 Top 5 Risers")
    for _, row in risers.iterrows():
        flag = get_flag_url(row['Country'], size='w40')
        flag_img = f'<img src="{flag}" style="width: 32px; vertical-align: middle; margin-right: 10px; border-radius: 3px;">' if flag else ''
        st.markdown(
            f'''
            <div class="mover-card" style="text-align: left; border-left: 4px solid #7A8450;">
                {flag_img}
                <span style="font-weight: 700; color: #2D2A26;">{row['Country']}</span>
                <span style="float: right; color: #7A8450; font-weight: 700;">+{row['score_change']:.3f}</span>
                <div style="font-size: 0.85rem; color: #5C5650; margin-top: 0.3rem; padding-left: 42px;">
                    {row['score_start']:.2f} → {row['score_end']:.2f} · 
                    Rank #{int(row['rank_start'])} → #{int(row['rank_end'])}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

with col_f:
    st.markdown("#### 🔴 Top 5 Fallers")
    for _, row in fallers.iterrows():
        flag = get_flag_url(row['Country'], size='w40')
        flag_img = f'<img src="{flag}" style="width: 32px; vertical-align: middle; margin-right: 10px; border-radius: 3px;">' if flag else ''
        st.markdown(
            f'''
            <div class="mover-card" style="text-align: left; border-left: 4px solid #C8553D;">
                {flag_img}
                <span style="font-weight: 700; color: #2D2A26;">{row['Country']}</span>
                <span style="float: right; color: #C8553D; font-weight: 700;">{row['score_change']:.3f}</span>
                <div style="font-size: 0.85rem; color: #5C5650; margin-top: 0.3rem; padding-left: 42px;">
                    {row['score_start']:.2f} → {row['score_end']:.2f} · 
                    Rank #{int(row['rank_start'])} → #{int(row['rank_end'])}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

# Turkey context
if 'Turkiye' in movers['Country'].values:
    tr = movers[movers['Country'] == 'Turkiye'].iloc[0]
    tr_rank_among_movers = (movers['score_change'] < tr['score_change']).sum() + 1
    st.markdown(
        f'''
        <div class="insight-card">
        🇹🇷 <b>Turkey</b>: {tr['score_start']:.2f} → {tr['score_end']:.2f} 
        (<b>{tr['score_change']:+.3f}</b>) · 
        Rank #{int(tr['rank_start'])} → #{int(tr['rank_end'])} 
        (<b>{int(tr['rank_change']):+d} positions</b>) · 
        Ranked <b>#{tr_rank_among_movers}</b> out of {len(movers)} countries by score change.
        </div>
        ''',
        unsafe_allow_html=True
    )


# === SECTION 4: REGIONAL HEATMAP ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🔥 Regional Heat — Score by Year")
st.caption("Darker red = lower happiness, darker green = higher. Patterns reveal regional shifts.")

heatmap_data = regional.pivot(index='Regional indicator', columns='Year', values='mean_score')
# Sort regions by latest year score
heatmap_data = heatmap_data.sort_values(last_year, ascending=False)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale=[
        [0, '#C8553D'],
        [0.5, '#F4E3C2'],
        [1, '#7A8450'],
    ],
    text=heatmap_data.round(2).values,
    texttemplate='%{text}',
    textfont={'size': 11, 'color': '#2D2A26'},
    hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>',
    colorbar=dict(title='Avg. Score', thickness=12, len=0.7),
))

fig_heatmap.update_layout(
    height=420,
    plot_bgcolor='#FAF3E0',
    paper_bgcolor='#FAF3E0',
    xaxis=dict(side='top', tickfont=dict(size=11)),
    yaxis=dict(tickfont=dict(size=11)),
    margin=dict(l=20, r=20, t=60, b=20),
)
st.plotly_chart(fig_heatmap, use_container_width=True)


# === SECTION 5: KPI EVOLUTION ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 📊 How Has Each KPI Evolved Globally?")
st.caption("World averages for the 6 happiness components over time.")

kpi_evolution = df.groupby('Year')[KDS_METRICS].mean().reset_index()

KPI_DISPLAY = {
    'GDP per capita': ('💰 GDP per Capita', '#C8553D'),
    'Social support': ('🤝 Social Support', '#7A8450'),
    'Healthy life expectancy': ('❤️ Life Expectancy', '#E8A87C'),
    'Freedom to make life choices': ('🕊️ Freedom', '#A8C09A'),
    'Generosity': ('🎁 Generosity', '#A14A2A'),
    'Perceptions of corruption': ('⚖️ Corruption Perception', '#9B5D3C'),
}

# 2x3 grid of mini-charts
metric_cols = st.columns(3)
for i, metric in enumerate(KDS_METRICS):
    with metric_cols[i % 3]:
        label, color = KPI_DISPLAY[metric]
        fig_mini = go.Figure()
        fig_mini.add_trace(go.Scatter(
            x=kpi_evolution['Year'],
            y=kpi_evolution[metric],
            mode='lines+markers',
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            fill='tozeroy',
            fillcolor='rgba(' + ', '.join(str(int(color[i:i+2], 16)) for i in (1, 3, 5)) + ', 0.2)',
            hovertemplate='%{x}: %{y:.3f}<extra></extra>',
        ))

        first_val = kpi_evolution.iloc[0][metric]
        last_val = kpi_evolution.iloc[-1][metric]
        change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

        fig_mini.update_layout(
            title=dict(
                text=f"<b>{label}</b><br><span style='font-size: 0.8em; color: #5C5650;'>"
                     f"{first_year}: {first_val:.2f} → {last_year}: {last_val:.2f} "
                     f"({change_pct:+.1f}%)</span>",
                font=dict(size=12, color='#2D2A26'),
                x=0.5, xanchor='center',
            ),
            height=240,
            plot_bgcolor='#FAF3E0',
            paper_bgcolor='#FAF3E0',
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=True, gridcolor='#E8DCC0', tickfont=dict(size=9)),
            margin=dict(l=10, r=10, t=50, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_mini, use_container_width=True)


# === FOOTER ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    f"💡 Spanning {first_year}-{last_year} · "
    f"{df['Country'].nunique()} unique countries · "
    f"{len(df)} country-year observations"
)

