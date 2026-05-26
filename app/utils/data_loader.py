"""
Data Loader - CSV okuma ve temizleme
Streamlit cache ile birlikte hizli erisim saglar
"""
import pandas as pd
import streamlit as st
from pathlib import Path


# Veri yolu - repo kokunden hesapla
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "world_happiness_combined.csv"


@st.cache_data
def load_happiness_data() -> pd.DataFrame:
    """
    World Happiness Report 2015-2024 birlesik veriyi yukler.
    Avrupa locale (sep=; decimal=,) formatini handle eder.
    Ulke isimlerini standardize eder (Turkey -> Turkiye).
    """
    df = pd.read_csv(DATA_PATH, sep=';', decimal=',')

    # Ulke ismi standardizasyonu
    df['Country'] = df['Country'].replace({'Turkey': 'Turkiye'})

    # Eksik Regional indicator dolduralim (sadece 3 satir)
    region_fixes = {
        'Greece': 'Western Europe',
        'Cyprus': 'Western Europe',
        'Gambia': 'Sub-Saharan Africa',
    }
    for country, region in region_fixes.items():
        mask = (df['Country'] == country) & (df['Regional indicator'].isnull())
        df.loc[mask, 'Regional indicator'] = region

    return df


@st.cache_data
def get_latest_year(df: pd.DataFrame) -> int:
    """En guncel yili dondurur (genelde 2024)."""
    return int(df['Year'].max())


@st.cache_data
def get_year_data(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Belirli bir yilin verisini dondurur."""
    return df[df['Year'] == year].copy()


@st.cache_data
def get_country_history(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """Bir ulkenin tum yillarini dondurur."""
    return df[df['Country'] == country].sort_values('Year').copy()


@st.cache_data
def get_country_list(df: pd.DataFrame) -> list:
    """Alfabetik ulke listesini dondurur."""
    return sorted(df['Country'].unique().tolist())


@st.cache_data
def get_region_list(df: pd.DataFrame) -> list:
    """Bolge listesini dondurur."""
    return sorted(df['Regional indicator'].dropna().unique().tolist())
