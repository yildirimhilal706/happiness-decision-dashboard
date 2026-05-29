"""
Clusters Page
K-means clustering of countries + PCA 2D visualization + radar profiles
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from math import pi

from utils.data_loader import load_happiness_data
from utils.profiles import KDS_METRICS, CLUSTER_NAMES, CLUSTER_COLORS
from utils.clustering import (
    compute_country_profiles, run_clustering, find_nearest_countries
)
from utils.flags import get_flag_url


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Clusters — Happiness Dashboard",
    page_icon="🔬",
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
    .cluster-card {
        background: #F4E3C2;
        border-radius: 16px;
        padding: 1.3rem 1rem;
        text-align: center;
        border-top: 6px solid;
        height: 100%;
    }
    .cluster-name {
        font-weight: 700;
        font-size: 1.05rem;
        color: #2D2A26;
        margin: 0.5rem 0 0.3rem 0;
    }
    .cluster-count {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2D2A26;
    }
    .cluster-label {
        font-size: 0.8rem;
        color: #5C5650;
    }
    .cluster-examples {
        font-size: 0.78rem;
        color: #7A8450;
        margin-top: 0.8rem;
        line-height: 1.4;
    }
    .divider {
        margin: 2.5rem 0 1.5rem 0;
        border-top: 1px dashed #C8B79D;
    }
</style>
""", unsafe_allow_html=True)


# === LOAD + CLUSTER ===
df = load_happiness_data()
country_profiles = compute_country_profiles(df, min_years=5)
cluster_results = run_clustering(country_profiles, k=4)

labels = cluster_results['labels']
pca_coords = cluster_results['pca_coords']
explained_var = cluster_results['explained_variance']

# Build full df with cluster assignments
country_profiles_df = country_profiles.copy()
country_profiles_df['Cluster'] = labels
country_profiles_df['Cluster_Name'] = [CLUSTER_NAMES[l] for l in labels]
country_profiles_df['PC1'] = pca_coords[:, 0]
country_profiles_df['PC2'] = pca_coords[:, 1]


# === HERO ===
st.markdown('<div class="hero-title">Country Clusters</div>', unsafe_allow_html=True)
st.caption(
    "K-means clustering reveals 4 distinct country archetypes based on 10-year average profiles. "
    f"Variance retained: {(explained_var[0] + explained_var[1])*100:.1f}% in 2D."
)


# === CLUSTER OVERVIEW CARDS ===
CLUSTER_META = {
    0: {'emoji': '⚖️', 'desc': 'Wealthy but distrustful — strong economy, weak freedom & generosity'},
    1: {'emoji': '🏗️', 'desc': 'Low income, weak institutions — Sub-Saharan & conflict zones'},
    2: {'emoji': '🏆', 'desc': 'Established prosperity — Nordics, Western Europe, ANZ'},
    3: {'emoji': '🌱', 'desc': 'Emerging values — moderate income, high generosity'},
}

cluster_sizes = country_profiles_df.groupby('Cluster').size().to_dict()
cluster_examples = {}
for cid in range(4):
    members = country_profiles_df[country_profiles_df['Cluster'] == cid].index.tolist()
    cluster_examples[cid] = sorted(members)[:5]


st.markdown("### 🎭 The Four Archetypes")
cols = st.columns(4)
for i, cid in enumerate(sorted(CLUSTER_META.keys())):
    with cols[i]:
        color = CLUSTER_COLORS[cid]
        examples = ', '.join(cluster_examples[cid])
        st.markdown(
            f'''
            <div class="cluster-card" style="border-top-color: {color};">
                <div style="font-size: 2.4rem;">{CLUSTER_META[cid]['emoji']}</div>
                <div class="cluster-name" style="color: {color};">{CLUSTER_NAMES[cid]}</div>
                <div class="cluster-count">{cluster_sizes[cid]}</div>
                <div class="cluster-label">countries</div>
                <div class="cluster-examples">
                    <i>{CLUSTER_META[cid]['desc']}</i><br><br>
                    e.g. {examples}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )


# === PCA SCATTER PLOT ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🗺️ Cluster Map — PCA 2D Projection")
st.caption(
    f"Each dot is a country. PC1 ({explained_var[0]*100:.1f}%) = Prosperity axis (GDP + health + social). "
    f"PC2 ({explained_var[1]*100:.1f}%) = Social character (generosity + freedom - corruption)."
)

fig_pca = go.Figure()

# Plot each cluster
for cid in sorted(CLUSTER_META.keys()):
    cluster_data = country_profiles_df[country_profiles_df['Cluster'] == cid]
    fig_pca.add_trace(go.Scatter(
        x=cluster_data['PC1'],
        y=cluster_data['PC2'],
        mode='markers',
        name=CLUSTER_NAMES[cid],
        marker=dict(
            size=10,
            color=CLUSTER_COLORS[cid],
            line=dict(color='white', width=1.5),
        ),
        text=cluster_data.index,
        hovertemplate='<b>%{text}</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>',
    ))

# Highlight Turkey
if 'Turkiye' in country_profiles_df.index:
    tr = country_profiles_df.loc['Turkiye']
    fig_pca.add_trace(go.Scatter(
        x=[tr['PC1']],
        y=[tr['PC2']],
        mode='markers+text',
        name='🇹🇷 Turkey',
        marker=dict(
            symbol='star',
            size=22,
            color='#2D2A26',
            line=dict(color='#E8A87C', width=2.5),
        ),
        text=['Turkey'],
        textposition='top center',
        textfont=dict(size=13, color='#2D2A26'),
        hovertemplate='<b>Turkey</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>',
    ))

# Label some notable countries
notable_countries = ['Finland', 'Denmark', 'United States', 'Germany', 'China', 'Brazil',
                     'India', 'Afghanistan', 'Singapore', 'Greece', 'Costa Rica']
for country in notable_countries:
    if country in country_profiles_df.index:
        row = country_profiles_df.loc[country]
        fig_pca.add_annotation(
            x=row['PC1'], y=row['PC2'],
            text=country,
            showarrow=False,
            xshift=8, yshift=8,
            font=dict(size=10, color='#2D2A26'),
            xanchor='left',
        )

fig_pca.update_layout(
    height=600,
    plot_bgcolor='#FAF3E0',
    paper_bgcolor='#FAF3E0',
    xaxis=dict(
        title=f'PC1 — Prosperity Axis ({explained_var[0]*100:.1f}%)',
        showgrid=True, gridcolor='#E8DCC0', zeroline=True, zerolinecolor='#C8B79D',
    ),
    yaxis=dict(
        title=f'PC2 — Social Character ({explained_var[1]*100:.1f}%)',
        showgrid=True, gridcolor='#E8DCC0', zeroline=True, zerolinecolor='#C8B79D',
    ),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
        bgcolor='rgba(244, 227, 194, 0.7)',
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)
st.plotly_chart(fig_pca, use_container_width=True)


# === RADAR CHART: 4 CLUSTER PROFILES ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🎯 Cluster Profiles — Side by Side")
st.caption("How each cluster scores on the 6 happiness KPIs (normalized).")

# Compute means per cluster
cluster_means = country_profiles_df.groupby('Cluster')[
    [f'{m}_norm' for m in KDS_METRICS]
].mean()

categories = ['GDP', 'Social Support', 'Life Expectancy', 'Freedom', 'Generosity', 'Low Corruption']

fig_radar = go.Figure()

for cid in sorted(CLUSTER_META.keys()):
    values = cluster_means.loc[cid].values.tolist()
    values += values[:1]  # close the loop
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=f"{CLUSTER_NAMES[cid]} ({cluster_sizes[cid]})",
        line=dict(color=CLUSTER_COLORS[cid], width=2.5),
        fillcolor=CLUSTER_COLORS[cid],
        opacity=0.25,
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1], gridcolor='#E8DCC0', tickfont=dict(size=10)),
        angularaxis=dict(gridcolor='#E8DCC0', tickfont=dict(size=11, color='#2D2A26')),
        bgcolor='#FAF3E0',
    ),
    paper_bgcolor='#FAF3E0',
    height=520,
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=-0.12, xanchor='center', x=0.5),
)
st.plotly_chart(fig_radar, use_container_width=True)


# === TURKEY'S NEIGHBORS ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🇹🇷 Turkey's Profile Neighbors")
st.caption("The 10 countries most similar to Turkey by Euclidean distance across all 6 KPIs.")

if 'Turkiye' in country_profiles.index:
    neighbors = find_nearest_countries(country_profiles, 'Turkiye', n=10)
    neighbors['Cluster'] = neighbors['Country'].map(
        lambda c: CLUSTER_NAMES[country_profiles_df.loc[c, 'Cluster']]
    )
    neighbors['Flag'] = neighbors['Country'].apply(get_flag_url)
    neighbors['Distance'] = neighbors['Distance'].round(3)

    display_neighbors = neighbors[['Flag', 'Country', 'Cluster', 'Distance']].rename(
        columns={'Cluster': 'Archetype'}
    )

    st.dataframe(
        display_neighbors,
        column_config={
            "Flag": st.column_config.ImageColumn("", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )

    tr_cluster_id = int(country_profiles_df.loc['Turkiye', 'Cluster'])
    tr_cluster_name = CLUSTER_NAMES[tr_cluster_id]
    same_cluster_count = sum(1 for _, row in neighbors.iterrows()
                             if CLUSTER_NAMES[country_profiles_df.loc[row['Country'], 'Cluster']] == tr_cluster_name)

    st.info(
        f"Turkey belongs to **{tr_cluster_name}** ({cluster_sizes[tr_cluster_id]} countries). "
        f"{same_cluster_count} of the top 10 neighbors are in the same archetype — "
        f"the rest are profile-similar but from neighboring clusters."
    )


# === CLUSTER DEEP DIVE ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 🔍 Cluster Deep Dive")
st.caption("Pick a cluster to see all its members.")

selected_cluster = st.selectbox(
    "Choose a cluster",
    options=list(range(4)),
    format_func=lambda x: f"{CLUSTER_META[x]['emoji']} {CLUSTER_NAMES[x]} ({cluster_sizes[x]} countries)",
)

cluster_members = country_profiles_df[
    country_profiles_df['Cluster'] == selected_cluster
].sort_index()

st.markdown(f"**{cluster_sizes[selected_cluster]} countries** in this archetype:")

# Show in columns, 6 per row
members_list = cluster_members.index.tolist()
n_cols = 6
rows = [members_list[i:i+n_cols] for i in range(0, len(members_list), n_cols)]

for row_countries in rows:
    cols = st.columns(n_cols)
    for i, country in enumerate(row_countries):
        with cols[i]:
            flag = get_flag_url(country, size='w40')
            flag_img = f'<img src="{flag}" style="width: 28px; vertical-align: middle; margin-right: 6px;">' if flag else ''
            highlight = 'background: #FAE8D0; border-radius: 6px; padding: 4px 6px;' if country == 'Turkiye' else ''
            st.markdown(
                f'<div style="{highlight} font-size: 0.85rem;">{flag_img}{country}</div>',
                unsafe_allow_html=True
            )


# === FOOTER ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    f"💡 K-means with k=4 · {len(country_profiles)} countries clustered · "
    f"min 5 years of data required · "
    f"PCA retains {(explained_var[0] + explained_var[1])*100:.1f}% variance in 2 dimensions"
)
