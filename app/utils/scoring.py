"""
KDS Skorlama - Normalizasyon ve Agirlikli Skor Hesaplama
"""
import pandas as pd
from .profiles import KDS_METRICS, INVERSE_METRICS


def normalize_metrics(
    data: pd.DataFrame,
    metrics: list = None,
    inverse: list = None,
) -> pd.DataFrame:
    """
    Min-max normalizasyon. Inverse listesindeki metrikleri ters cevirir.

    Args:
        data: Ham veri (DataFrame)
        metrics: Normalize edilecek metrik listesi (default: KDS_METRICS)
        inverse: Ters cevrilecek metrikler (default: INVERSE_METRICS)

    Returns:
        Yeni `<metric>_norm` kolonlari eklenmis DataFrame
    """
    if metrics is None:
        metrics = KDS_METRICS
    if inverse is None:
        inverse = INVERSE_METRICS

    df_norm = data.copy()

    for metric in metrics:
        col_min = df_norm[metric].min()
        col_max = df_norm[metric].max()

        # Sifira bolme korumasi
        if col_max == col_min:
            df_norm[f'{metric}_norm'] = 0.5
            continue

        normalized = (df_norm[metric] - col_min) / (col_max - col_min)

        if metric in inverse:
            normalized = 1 - normalized

        df_norm[f'{metric}_norm'] = normalized

    return df_norm


def calculate_kds_score(
    df_normalized: pd.DataFrame,
    weights: dict,
    metrics: list = None,
) -> pd.DataFrame:
    """
    Normalize edilmis veriye agirlik uygular, KDS skoru ve sira uretir.

    Args:
        df_normalized: normalize_metrics ciktisi
        weights: dict {metric_name: weight} - toplam 1.0 olmali
        metrics: Hangi metrikler hesaba katilacak (default: KDS_METRICS)

    Returns:
        `KDS_score` (0-10) ve `KDS_rank` eklenmis, skora gore sirali DataFrame
    """
    if metrics is None:
        metrics = KDS_METRICS

    df_result = df_normalized.copy()
    df_result['KDS_score'] = 0.0

    for metric in metrics:
        norm_col = f'{metric}_norm'
        df_result['KDS_score'] += df_result[norm_col] * weights[metric]

    # 0-1 araligini 0-10'a cevir (gorsel olarak yorumlanabilir)
    df_result['KDS_score'] *= 10

    df_result['KDS_rank'] = df_result['KDS_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    return df_result.sort_values('KDS_score', ascending=False).reset_index(drop=True)


def validate_weights(weights: dict, tolerance: float = 0.01) -> tuple:
    """
    Agirliklarin toplamini kontrol eder.

    Returns:
        (is_valid: bool, total: float)
    """
    total = sum(weights.values())
    is_valid = abs(total - 1.0) <= tolerance
    return is_valid, total


def normalize_weights(weights: dict) -> dict:
    """Agirliklarin toplami 1.0 olacak sekilde olcekler."""
    total = sum(weights.values())
    if total == 0:
        return weights
    return {k: v / total for k, v in weights.items()}
