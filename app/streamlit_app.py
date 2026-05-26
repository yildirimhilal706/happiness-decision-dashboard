"""
Happiness Decision Dashboard - Main page
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_happiness_data, get_latest_year, get_year_data
from utils.profiles import (
    PROFILES, PROFILE_DESCRIPTIONS, KDS_METRICS, INVERSE_METRICS
)
from utils.scoring import normalize_metrics, calculate_kds_score, normalize_weights
from utils.flags import get_country_iso3, get_flag_url


st.set_page_config(
    page_title="Happiness Decision Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


COLORS = {
    'terra': '#C8553D', 'sand': '#F4E3C2', 'paper': '#FAF3E0',
    'espresso': '#2D2A26', 'olive': '#7A8450', 'amber': '#E8A87C',
    'rust': '#A14A2A', 'sage': '#A8C09A',
}

PROFILE_STYLE = {
    'Student':      {'emoji': '🎓', 'color': '#7A8450'},
    'Retiree':      {'emoji': '🌅', 'color': '#E8A87C'},
    'Family':       {'emoji': '🏡', 'color': '#A8C09A'},
    'Entrepreneur': {'emoji': '💼', 'color': '#C8553D'},
    'Balanced':     {'emoji': '⚖️', 'color': '#A14A2A'},
}

PROFILE_DESC_EN = {
    'Student': 'Freedom & social support take priority — ideal for studying abroad.',
    'Retiree': 'Health & low corruption matter most — for a peaceful late life.',
    'Family': 'Balanced social support & healthcare — raising children.',
    'Entrepreneur': 'Economic strength & freedom — starting a business.',
    'Balanced': 'All metrics equal — baseline reference.',
}


st.markdown("""
<style>
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #C8553D 0%, #E8A87C 50%, #7A8450 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 1.15rem; color: #5C5650;
        margin-bottom: 2rem; line-height: 1.5;
    }
    .profile-card {
        background: #F4E3C2; border-radius: 16px;
        padding: 1.2rem 1rem; text-align: center;
        border: 2px solid transparent; transition: all 0.2s ease;
        height: 100%;
    }
    .profile-card-active {
        border-color: #C8553D !important;
        background: #FAE8D0 !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.6rem; color: #2D2A26; }
    [data-testid="stMetricLabel"] { color: #5C5650; }
    .divider {
        margin: 2.5rem 0 1.5rem 0;
        border-top: 1px dashed #C8B79D;
    }
</style>
""", unsafe_allow_html=True)


df = load_happiness_data()
latest_year = get_latest_year(df)


# === HERO ===
st.markdown('<div class="hero-title">Where Should You Live?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'A <b>decision-support dashboard</b> built on the World Happiness Report (2015-2024). '
    'Choose your own priorities — see the world re-rank itself through your lens.'
    '</div>',
    unsafe_allow_html=True
)


# === SIDEBAR ===
st.sidebar.markdown("### ⚙️ Settings")
year_options = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("📅 Year", year_options, index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Profile")
profile_choice = st.sidebar.radio(
    "Profile",
    options=list(PROFILES.keys()) + ['Custom'],
    label_visibility="collapsed",
    index=4,
)

if profile_choice != 'Custom':
    st.sidebar.caption(PROFILE_DESC_EN[profile_choice])

st.sidebar.markdown("### ⚖️ Weights")
st.sidebar.caption("Adjust sliders to build your own profile")

if profile_choice == 'Custom':
    default_weights = {m: 1/6 for m in KDS_METRICS}
else:
    default_weights = PROFILES[profile_choice]

METRIC_LABELS_EN = {
    'GDP per capita': 'GDP per Capita',
    'Social support': 'Social Support',
    'Healthy life expectancy': 'Healthy Life Expectancy',
    'Freedom to make life choices': 'Freedom of Choice',
    'Generosity': 'Generosity',
    'Perceptions of corruption': 'Low Corruption',
}

user_weights = {}
for metric in KDS_METRICS:
    label = METRIC_LABELS_EN[metric]
    user_weights[metric] = st.sidebar.slider(
        label, min_value=0, max_value=100,
        value=int(default_weights[metric] * 100),
        step=5, key=f"slider_{metric}",
    )

total_weight = sum(user_weights.values())
if total_weight == 0:
    st.sidebar.error("⚠️ Total cannot be 0")
    st.stop()

weights_normalized = normalize_weights({m: w/100 for m, w in user_weights.items()})

if total_weight != 100:
    st.sidebar.info(f"Total: **{total_weight}** → auto-normalized")


df_year = get_year_data(df, selected_year)
df_year_norm = normalize_metrics(df_year)
scored = calculate_kds_score(df_year_norm, weights_normalized)


# === WORLD MAP ===
st.markdown("## 🗺️ The World Through Your Eyes")
st.caption(
    f"Darker shades = higher quality of life under the **{profile_choice}** profile. "
    f"({selected_year} data)"
)

scored['iso3'] = scored['Country'].apply(get_country_iso3)
map_df = scored.dropna(subset=['iso3']).copy()

fig_map = px.choropleth(
    map_df,
    locations='iso3',
    color='KDS_score',
    hover_name='Country',
    hover_data={'iso3': False, 'KDS_score': ':.2f', 'KDS_rank': True, 'Ranking': True},
    color_continuous_scale=[
        [0, '#F4E3C2'], [0.3, '#E8A87C'],
        [0.6, '#C8553D'], [1, '#7A8450'],
    ],
    labels={'KDS_score': 'KDS Score', 'KDS_rank': 'Your Rank', 'Ranking': 'Official Rank'},
)
fig_map.update_layout(
    height=500, margin=dict(l=0, r=0, t=0, b=0),
    geo=dict(showframe=False, showcoastlines=True,
             coastlinecolor='#C8B79D', bgcolor='#FAF3E0',
             landcolor='#F4E3C2', projection_type='natural earth'),
    paper_bgcolor='#FAF3E0',
    coloraxis_colorbar=dict(title=None, thickness=12, len=0.7),
)
st.plotly_chart(fig_map, use_container_width=True)


# === PROFILE CARDS ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("## 👥 Profiles")
st.caption("Each profile represents a different life priority. Pick one in the sidebar — the map and ranking update instantly.")

cols = st.columns(5)
for i, (pname, style) in enumerate(PROFILE_STYLE.items()):
    with cols[i]:
        active_class = 'profile-card-active' if pname == profile_choice else ''
        st.markdown(
            f'<div class="profile-card {active_class}">'
            f'<div style="font-size: 2.2rem;">{style["emoji"]}</div>'
            f'<div style="font-weight: 700; color: {style["color"]}; margin: 0.4rem 0;">{pname}</div>'
            f'<div style="font-size: 0.85rem; color: #5C5650;">{PROFILE_DESC_EN[pname]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# === TURKEY SPOTLIGHT ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("## 🇹🇷 Turkey Spotlight")

tr_row = scored[scored['Country'] == 'Turkiye']
if len(tr_row) > 0:
    tr_kds_rank = int(tr_row.iloc[0]['KDS_rank'])
    tr_kds_score = tr_row.iloc[0]['KDS_score']
    tr_official_rank = int(df_year[df_year['Country'] == 'Turkiye']['Ranking'].values[0])
    tr_happiness = df_year[df_year['Country'] == 'Turkiye']['Happiness score'].values[0]
    diff = tr_official_rank - tr_kds_rank

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Official WHR Rank", f"#{tr_official_rank} / {len(df_year)}",
                  delta=f"Score: {tr_happiness:.2f}")
    with c2:
        st.metric(f"Your KDS Rank ({profile_choice})", f"#{tr_kds_rank} / {len(df_year)}",
                  delta=f"Score: {tr_kds_score:.2f}/10")
    with c3:
        if diff > 0:
            msg = f"{diff} positions BETTER in this profile"
            delta_color = "normal"
        elif diff < 0:
            msg = f"{abs(diff)} positions WORSE in this profile"
            delta_color = "inverse"
        else:
            msg = "Same position"
            delta_color = "off"
        st.metric("Movement", f"{diff:+d}", delta=msg, delta_color=delta_color)
else:
    st.info(f"Turkey is not present in {selected_year} data.")


# === TOP 10 TABLE WITH FLAGS ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"## 🏆 Top 10 — {profile_choice} Profile ({selected_year})")

top10 = scored.head(10).copy()
top10['Flag'] = top10['Country'].apply(get_flag_url)
top10['KDS Score'] = top10['KDS_score'].round(2)
top10['Your Rank'] = top10['KDS_rank']
top10['Official Rank'] = top10['Ranking']
top10['Movement'] = top10.apply(
    lambda r: f"⬆ +{r['Ranking'] - r['KDS_rank']}" if r['Ranking'] > r['KDS_rank']
    else (f"⬇ {r['Ranking'] - r['KDS_rank']}" if r['Ranking'] < r['KDS_rank'] else "= same"),
    axis=1
)

display_top10 = top10[['Flag', 'Country', 'Your Rank', 'KDS Score', 'Official Rank', 'Movement']]

st.dataframe(
    display_top10,
    column_config={
        "Flag": st.column_config.ImageColumn("", width="small"),
        "Movement": st.column_config.TextColumn("Rank Movement", help="How your KDS rank differs from the official WHR rank"),
    },
    hide_index=True,
    use_container_width=True,
)


# === BIGGEST MOVERS — TWO-COLUMN LAYOUT (NO OVERLAP) ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("## 📊 Biggest Movers")
st.caption(
    f"Countries whose ranking changes the most under the **{profile_choice}** profile. "
    "Green = better in your view · Red = better in the official ranking."
)

# Top 10 movers (changed from 12 to 10 - cleaner)
all_moves = scored[['Country', 'KDS_rank', 'Ranking']].copy()
all_moves['Movement'] = all_moves['Ranking'] - all_moves['KDS_rank']
biggest_movers = all_moves.reindex(
    all_moves['Movement'].abs().sort_values(ascending=False).index
).head(10).reset_index(drop=True)

# Layout: equal-spaced labels on both sides via positional y-values
# Sort by official rank for left column, by KDS rank for right column
left_sorted = biggest_movers.sort_values('Ranking').reset_index(drop=True)
right_sorted = biggest_movers.sort_values('KDS_rank').reset_index(drop=True)

n = len(biggest_movers)
# Equal y-positions for clean labels (0 to n-1)
left_y_positions = {row['Country']: i for i, row in left_sorted.iterrows()}
right_y_positions = {row['Country']: i for i, row in right_sorted.iterrows()}

fig_slope = go.Figure()

# Background line columns (visual guides)
fig_slope.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=n - 0.5,
                    line=dict(color='#C8B79D', width=2))
fig_slope.add_shape(type="line", x0=1, x1=1, y0=-0.5, y1=n - 0.5,
                    line=dict(color='#C8B79D', width=2))

for _, row in biggest_movers.iterrows():
    movement = row['Movement']
    country = row['Country']
    left_y = left_y_positions[country]
    right_y = right_y_positions[country]

    if movement > 0:
        color = '#7A8450'  # better in KDS
    elif movement < 0:
        color = '#C8553D'  # better in official
    else:
        color = '#A14A2A'

    # The connecting line
    fig_slope.add_trace(go.Scatter(
        x=[0, 1],
        y=[left_y, right_y],
        mode='lines+markers',
        line=dict(color=color, width=2.5),
        marker=dict(size=11, color=color, line=dict(color='#FAF3E0', width=2)),
        hoverinfo='text',
        hovertext=(f"<b>{country}</b><br>"
                   f"Official: #{int(row['Ranking'])}<br>"
                   f"Your KDS: #{int(row['KDS_rank'])}<br>"
                   f"Movement: {int(movement):+d}"),
        showlegend=False,
    ))

    # Left label (official rank)
    fig_slope.add_annotation(
        x=-0.03, y=left_y,
        text=f"<b>{country}</b>  #{int(row['Ranking'])}",
        showarrow=False,
        xanchor='right',
        font=dict(size=12, color='#2D2A26'),
    )
    # Right label (KDS rank)
    fig_slope.add_annotation(
        x=1.03, y=right_y,
        text=f"#{int(row['KDS_rank'])}  <b>{country}</b>",
        showarrow=False,
        xanchor='left',
        font=dict(size=12, color='#2D2A26'),
    )

fig_slope.update_layout(
    height=max(450, n * 55),
    xaxis=dict(
        tickvals=[0, 1],
        ticktext=['<b>Official WHR Rank</b>', f'<b>Your KDS Rank ({profile_choice})</b>'],
        showgrid=False, zeroline=False,
        range=[-0.5, 1.5],
        side='top',
        tickfont=dict(size=14, color='#2D2A26'),
    ),
    yaxis=dict(
        showgrid=False, zeroline=False,
        showticklabels=False,
        autorange='reversed',
        range=[n - 0.3, -0.7],
    ),
    plot_bgcolor='#FAF3E0',
    paper_bgcolor='#FAF3E0',
    margin=dict(l=10, r=10, t=60, b=20),
)
st.plotly_chart(fig_slope, use_container_width=True)


# === FOOTER ===
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    f"💡 **Data:** World Happiness Report 2015-2024 (Kaggle) · "
    f"**Method:** Min-max normalize + weighted scoring · "
    f"**Year:** {selected_year} · **Profile:** {profile_choice}"
)
