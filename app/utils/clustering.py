"""
K-means Clustering + PCA Gorselli rendering icin yardimcilar
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import streamlit as st

from .profiles import KDS_METRICS
from .scoring import normalize_metrics


@st.cache_data
def compute_country_profiles(df: pd.DataFrame, min_years: int = 5) -> pd.DataFrame:
    """
    Her ulkenin 10 yillik ortalama normalize edilmis profilini cikarir.
    En az `min_years` yil verisi olan ulkeleri dahil eder.
    """
    df_all_norm = normalize_metrics(df)
    norm_cols = [f'{m}_norm' for m in KDS_METRICS]

    country_profiles = df_all_norm.groupby('Country')[norm_cols].mean()

    # Yeterli yil verisi olan ulkeler
    year_counts = df.groupby('Country')['Year'].count()
    valid_countries = year_counts[year_counts >= min_years].index
    country_profiles = country_profiles.loc[valid_countries]

    return country_profiles


@st.cache_data
def run_clustering(country_profiles: pd.DataFrame, k: int = 4, random_state: int = 42):
    """
    K-means clustering + PCA 2D projection.

    Returns:
        dict with keys: labels, pca_coords, explained_variance, kmeans, pca
    """
    X = country_profiles.values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(X_scaled)

    return {
        'labels': labels,
        'pca_coords': pca_coords,
        'explained_variance': pca.explained_variance_ratio_,
        'kmeans': kmeans,
        'pca': pca,
        'feature_names': list(country_profiles.columns),
    }


def find_nearest_countries(
    country_profiles: pd.DataFrame,
    target_country: str,
    n: int = 15,
) -> pd.DataFrame:
    """
    Bir ulkeye en yakin n ulkeyi Euclidean mesafeyle bulur.
    """
    from scipy.spatial.distance import cdist

    if target_country not in country_profiles.index:
        return pd.DataFrame()

    target_profile = country_profiles.loc[target_country].values.reshape(1, -1)
    distances = cdist(target_profile, country_profiles.values)[0]

    distance_df = pd.DataFrame({
        'Country': country_profiles.index,
        'Distance': distances,
    })
    distance_df = distance_df[distance_df['Country'] != target_country]
    return distance_df.sort_values('Distance').head(n).reset_index(drop=True)
