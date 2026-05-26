"""
Bayrak Helper - Ulke adlarini flagcdn.com URL'lerine cevirir
"""
import pycountry
from functools import lru_cache


# Dataset'te WHR isimleri pycountry ile uyusmayabiliyor - manuel eslesme
COUNTRY_NAME_OVERRIDES = {
    'Turkiye': 'TR',
    'Turkey': 'TR',
    'United States': 'US',
    'United Kingdom': 'GB',
    'Russia': 'RU',
    'South Korea': 'KR',
    'North Korea': 'KP',
    'Czech Republic': 'CZ',
    'Czechia': 'CZ',
    'Slovakia': 'SK',
    'Macedonia': 'MK',
    'North Macedonia': 'MK',
    'Bosnia and Herzegovina': 'BA',
    'Hong Kong S.A.R. of China': 'HK',
    'Hong Kong': 'HK',
    'Taiwan Province of China': 'TW',
    'Taiwan': 'TW',
    'Palestinian Territories': 'PS',
    'Palestine': 'PS',
    'Congo (Brazzaville)': 'CG',
    'Congo (Kinshasa)': 'CD',
    'Ivory Coast': 'CI',
    "Cote d'Ivoire": 'CI',
    'Argelia': 'DZ',
    'Algeria': 'DZ',
    'Iran': 'IR',
    'Syria': 'SY',
    'Vietnam': 'VN',
    'Laos': 'LA',
    'Tanzania': 'TZ',
    'Venezuela': 'VE',
    'Bolivia': 'BO',
    'Moldova': 'MD',
    'Kosovo': 'XK',  # Resmi ISO kodu yok, XK pratik kullanim
    'Eswatini': 'SZ',
    'Swaziland': 'SZ',
    'Cape Verde': 'CV',
    'Myanmar': 'MM',
    'Burma': 'MM',
    'East Timor': 'TL',
    'Timor-Leste': 'TL',
    'North Cyprus': 'CY',
    'Somaliland region': 'SO',
    'Somaliland Region': 'SO',
}


@lru_cache(maxsize=300)
def get_country_iso2(country_name: str) -> str:
    """
    Ulke adindan ISO 3166-1 alpha-2 kodu uretir.
    Once manuel override'a, sonra pycountry'ye bakar.
    """
    if country_name in COUNTRY_NAME_OVERRIDES:
        return COUNTRY_NAME_OVERRIDES[country_name]

    # pycountry ile dene
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_2
    except (LookupError, IndexError):
        return None


@lru_cache(maxsize=300)
def get_country_iso3(country_name: str) -> str:
    """Choropleth icin ISO alpha-3 kodu (plotly bunu istiyor)."""
    iso2 = get_country_iso2(country_name)
    if iso2 is None:
        return None
    try:
        country = pycountry.countries.get(alpha_2=iso2)
        return country.alpha_3 if country else None
    except Exception:
        return None


def get_flag_url(country_name: str, size: str = 'w40') -> str:
    """
    flagcdn.com URL'i dondurur.

    Args:
        country_name: WHR'deki ulke adi
        size: 'w20', 'w40', 'w80', 'w160', 'w320'

    Returns:
        URL veya None (eslesme yoksa)
    """
    iso2 = get_country_iso2(country_name)
    if iso2 is None:
        return None
    return f"https://flagcdn.com/{size}/{iso2.lower()}.png"


def get_flag_emoji(country_name: str) -> str:
    """
    Emoji bayrak (yedek olarak, flagcdn yuklenmezse).
    Iki harfli ISO kodunu regional indicator karakterlerine cevirir.
    """
    iso2 = get_country_iso2(country_name)
    if iso2 is None:
        return '🏳️'
    # ISO kodunu unicode regional indicator karaktererine cevir
    return ''.join(chr(ord(c) + 127397) for c in iso2.upper())
