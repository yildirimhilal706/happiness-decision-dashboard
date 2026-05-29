"""
Country Explorer Page
Deep-dive on a single country: trends, KPI breakdown, similar countries, profile rankings
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import (
    load_happiness_data, get_latest_year, get_country_list, get_country_history
)
from utils.profiles import PROFILES, KDS_METRICS, INVERSE_METRICS
from utils.scoring import normalize_metrics, calculate_kds_score
from utils.flags import get_flag_url


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Country Explorer — Happiness Dashboard",
    page_icon="🌍",
    layout="wide",
)


# === CUSTOM CSS (matches main page) ===
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
    .country-hero {
        background: #F4E3C2;
        border-radius: 20px;
        padding: 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    .country-flag {
        width: 100px;
        height: auto;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .country-name {
        font-size: 2.4rem;
        font-weight: 700;
        color: #2D2A26;
        margin: 0;
    }
    .country-region {
        font-size: 1rem;
        color: #7A8450;
        margin-top: 0.2rem;
    }
    [data-testid="stMetricValue"] { font-size: 1.4rem; color: #2D2A26; }
    [data-testid="stMetricLabel"] { color: #5C5650; }
    .divider {
        margin: 2.5rem 0 1.5rem 0;
        border-top: 1px dashed #C8B79D;
    }
</style>
""", unsafe_allow_html=True)


# === LOAD DATA ===
df = load_happiness_data()
latest_year = get_latest_year(df)
countries = get_country_list(df)


# === HERO TITLE ===
st.markdown('<div class="hero-title">Country Explorer</div>', unsafe_allow_html=True)
st.caption("Deep dive on a single country — 10-year trends, KPI breakdown, and how it ranks under different life profiles.")


# === COUNTRY SELECTOR ===
default_idx = countries.index('Turkiye') if 'Turkiye' in countries else 0
selected_country = st.selectbox(
    "🔍 Choose a country",
    options=countries,
    index=default_idx,
)


# === COUNTRY HISTORY ===
history = get_country_history(df, selected_country)

if len(history) == 0:
    st.warning(f"No data available for {selected_country}.")
    st.stop()

latest = history.iloc[-1]
flag_url = get_flag_url(selected_country, size='w160')


# === HERO CARD ===
flag_html = f'<img src="{flag_url}" class="country-flag" alt="{selected_country} flag">' if flag_url else ''
region = latest.get('Regional indicator', 'Unknown region')

st.markdown(
    f'''
    <div class="country-hero">
        {flag_html}
        <div style="flex: 1;">
            <div class="country-name">{selected_country}</div>
            <div class="country-region">📍 {region}</div>
            <div style="margin-top: 0.8rem; color: #5C5650;">
                Latest data: <b>{int(latest['Year'])}</b> · 
                Happiness Score: <b>{latest['Happiness score']:.2f}</b> · 
                Official Rank: <b>#{int(latest['Ranking'])}</b>
            </div>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)


# === 10-YEAR TREND ===
st.markdown("### 📈 10-Year Trend")

col1, col2 = st.columns([2, 1])

with col1:
    fig_trend = go.Figure()

    # Happiness score line
    fig_trend.add_trace(go.Scatter(
        x=history['Year'],
        y=history['Happiness score'],
        mode='lines+markers',
        name='Happiness Score',
        line=dict(color='#C8553D', width=3),
        marker=dict(size=10, color='#C8553D'),
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>',
    ))

    # Average reference line (world avg per year for that subset)
    world_avg = df.groupby('Year')['Happiness score'].mean().reset_index()
    fig_trend.add_trace(go.Scatter(
        x=world_avg['Year'],
        y=world_avg['Happiness score'],
        mode='lines',
        name='World Average',
        line=dict(color='#A14A2A', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>World avg: %{y:.2f}<extra></extra>',
    ))

    fig_trend.update_layout(
        height=380,
        plot_bgcolor='#FAF3E0',
        paper_bgcolor='#FAF3E0',
        xaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Year'),
        yaxis=dict(showgrid=True, gridcolor='#E8DCC0', title='Happiness Score'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown("#### Movement")
    if len(history) >= 2:
        first = history.iloc[0]
        last = history.iloc[-1]
        score_change = last['Happiness score'] - first['Happiness score']
        rank_change = int(first['Ranking']) - int(last['Ranking'])

        st.metric(
            f"Score: {int(first['Year'])} → {int(last['Year'])}",
            f"{last['Happiness score']:.2f}",
            delta=f"{score_change:+.2f}",
        )

        st.metric(
            f"Rank: {int(first['Year'])} → {int(last['Year'])}",
            f"#{int(last['Ranking'])}",
            delta=f"{rank_change:+d} positions",
            delta_color="normal" if rank_change >= 0 else "inverse",
        )

        # Years of data
        st.metric("Years of data", len(history))


# === RADAR CHART: COUNTRY vs WORLD ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🎯 KPI Profile vs World Average")
st.caption(f"All values normalized to 0-1 scale. Higher = better (corruption is inverted).")

# Normalize all data for fair comparison
df_norm = normalize_metrics(df)
norm_cols = [f'{m}_norm' for m in KDS_METRICS]

# Country average (latest 3 years for stability)
recent_years = history.tail(3)
recent_norm = df_norm[df_norm['Country'] == selected_country].tail(3)
country_avg = recent_norm[norm_cols].mean()

# World average
world_avg_norm = df_norm[norm_cols].mean()

# Categories for radar
categories = ['GDP', 'Social Support', 'Life Expectancy', 'Freedom', 'Generosity', 'Low Corruption']

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=country_avg.values.tolist() + [country_avg.values[0]],
    theta=categories + [categories[0]],
    fill='toself',
    name=selected_country,
    line=dict(color='#C8553D', width=2.5),
    fillcolor='rgba(200, 85, 61, 0.25)',
))

fig_radar.add_trace(go.Scatterpolar(
    r=world_avg_norm.values.tolist() + [world_avg_norm.values[0]],
    theta=categories + [categories[0]],
    fill='toself',
    name='World Average',
    line=dict(color='#7A8450', width=2, dash='dash'),
    fillcolor='rgba(122, 132, 80, 0.15)',
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1], gridcolor='#E8DCC0'),
        angularaxis=dict(gridcolor='#E8DCC0'),
        bgcolor='#FAF3E0',
    ),
    paper_bgcolor='#FAF3E0',
    height=460,
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
)
st.plotly_chart(fig_radar, use_container_width=True)


# === KPI BREAKDOWN ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 📊 KPI Breakdown (Latest Year)")

kpi_cols = st.columns(3)
kpi_data = [
    ('💰 GDP per Capita', latest['GDP per capita'], df_norm['GDP per capita'].max()),
    ('🤝 Social Support', latest['Social support'], 1.0),
    ('❤️ Healthy Life Exp.', latest['Healthy life expectancy'], df['Healthy life expectancy'].max()),
    ('🕊️ Freedom of Choice', latest['Freedom to make life choices'], 1.0),
    ('🎁 Generosity', latest['Generosity'], 1.0),
    ('⚖️ Perceived Corruption', latest['Perceptions of corruption'], 1.0),
]

for i, (label, value, max_val) in enumerate(kpi_data):
    with kpi_cols[i % 3]:
        # Show world average for context
        col_name = label.split(' ', 1)[1] if ' ' in label else label
        # Match to original metric name
        metric_map = {
            'GDP per Capita': 'GDP per capita',
            'Social Support': 'Social support',
            'Healthy Life Exp.': 'Healthy life expectancy',
            'Freedom of Choice': 'Freedom to make life choices',
            'Generosity': 'Generosity',
            'Perceived Corruption': 'Perceptions of corruption',
        }
        orig_metric = metric_map.get(col_name, col_name)
        world_metric_avg = df[orig_metric].mean()
        diff_from_world = value - world_metric_avg

        st.metric(
            label,
            f"{value:.2f}",
            delta=f"{diff_from_world:+.2f} vs world",
            delta_color="normal" if (orig_metric != 'Perceptions of corruption' and diff_from_world > 0) or (orig_metric == 'Perceptions of corruption' and diff_from_world < 0) else "inverse",
        )


# === SIMILAR COUNTRIES ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"### 🤝 Most Similar Countries to {selected_country}")
st.caption("Based on Euclidean distance across all 6 KPIs, averaged over the last 5 years.")

# Build country profiles (avg of last 5 years, normalized)
recent_df = df_norm[df_norm['Year'] >= df_norm['Year'].max() - 4]
country_profiles = recent_df.groupby('Country')[norm_cols].mean()

if selected_country in country_profiles.index:
    target_profile = country_profiles.loc[selected_country].values
    distances = np.linalg.norm(country_profiles.values - target_profile, axis=1)

    distance_df = pd.DataFrame({
        'Country': country_profiles.index,
        'Distance': distances,
    })
    distance_df = distance_df[distance_df['Country'] != selected_country].sort_values('Distance').head(5)

    # Render similar countries as cards
    sim_cols = st.columns(5)
    for i, (_, row) in enumerate(distance_df.iterrows()):
        with sim_cols[i]:
            similar_flag = get_flag_url(row['Country'], size='w80')
            similar_row = df[df['Country'] == row['Country']]
            if len(similar_row) > 0:
                latest_sim = similar_row.iloc[-1]
                rank = int(latest_sim['Ranking'])
                score = latest_sim['Happiness score']
            else:
                rank, score = '?', '?'

            flag_img = f'<img src="{similar_flag}" style="width: 60px; border-radius: 4px; margin-bottom: 0.5rem;">' if similar_flag else ''

            st.markdown(
                f'''
                <div style="background: #F4E3C2; border-radius: 12px; padding: 1rem; text-align: center;">
                    {flag_img}
                    <div style="font-weight: 700; color: #2D2A26;">{row['Country']}</div>
                    <div style="font-size: 0.85rem; color: #7A8450; margin-top: 0.3rem;">
                        Rank #{rank} · Score {score:.2f}
                    </div>
                    <div style="font-size: 0.75rem; color: #A14A2A; margin-top: 0.4rem;">
                        Distance: {row['Distance']:.3f}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
else:
    st.info("Not enough data to compute similar countries.")


# === RANKING ACROSS PROFILES ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"### 👥 {selected_country}'s Rank Across Different Profiles")
st.caption("How would this country rank if we measured happiness through different life priorities?")

# Use latest year data
df_latest = df[df['Year'] == latest_year].copy()
df_latest_norm = normalize_metrics(df_latest)

profile_ranks = []
for pname, weights in PROFILES.items():
    scored = calculate_kds_score(df_latest_norm, weights)
    country_row = scored[scored['Country'] == selected_country]
    if len(country_row) > 0:
        profile_ranks.append({
            'Profile': pname,
            'Rank': int(country_row.iloc[0]['KDS_rank']),
            'Score': country_row.iloc[0]['KDS_score'],
        })

# Official rank for reference
official_rank = df_latest[df_latest['Country'] == selected_country]['Ranking'].values
if len(official_rank) > 0:
    profile_ranks.append({
        'Profile': 'Official WHR',
        'Rank': int(official_rank[0]),
        'Score': float(df_latest[df_latest['Country'] == selected_country]['Happiness score'].values[0]),
    })

if profile_ranks:
    rank_df = pd.DataFrame(profile_ranks)
    total_countries = len(df_latest)

    fig_profiles = go.Figure()

    colors_profile = {
        'Student': '#7A8450',
        'Retiree': '#E8A87C',
        'Family': '#A8C09A',
        'Entrepreneur': '#C8553D',
        'Balanced': '#A14A2A',
        'Official WHR': '#2D2A26',
    }
    bar_colors = [colors_profile.get(p, '#7A8450') for p in rank_df['Profile']]

    fig_profiles.add_trace(go.Bar(
        x=rank_df['Profile'],
        y=rank_df['Rank'],
        marker_color=bar_colors,
        text=[f"#{r}" for r in rank_df['Rank']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Rank: #%{y} / ' + str(total_countries) + '<extra></extra>',
    ))

    fig_profiles.update_layout(
        height=380,
        plot_bgcolor='#FAF3E0',
        paper_bgcolor='#FAF3E0',
        yaxis=dict(
            title='Rank (lower = better)',
            autorange='reversed',
            showgrid=True,
            gridcolor='#E8DCC0',
        ),
        xaxis=dict(title=''),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig_profiles, use_container_width=True)

    # Summary insight
    profile_only = rank_df[rank_df['Profile'] != 'Official WHR']
    if len(profile_only) > 1:
        best_profile = profile_only.loc[profile_only['Rank'].idxmin()]
        worst_profile = profile_only.loc[profile_only['Rank'].idxmax()]
        spread = worst_profile['Rank'] - best_profile['Rank']

        st.info(
            f"**{selected_country}** ranks #{best_profile['Rank']} under the **{best_profile['Profile']}** profile "
            f"(its strongest profile), but drops to #{worst_profile['Rank']} under **{worst_profile['Profile']}**. "
            f"That's a **{spread}-position spread** depending on what you value most in life."
        )
else:
    st.info("Profile rankings not available for this country.")


# === FOOTER ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    f"💡 Showing data for **{selected_country}** · "
    f"{len(history)} years of data ({int(history['Year'].min())}-{int(history['Year'].max())}) · "
    f"Region: {region}"
)
