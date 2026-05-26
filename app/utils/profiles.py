"""
Karar Destek Profilleri ve KPI Tanimlari
"""

# 6 KDS metrigi - veri setindeki kolon adlari
KDS_METRICS = [
    'GDP per capita',
    'Social support',
    'Healthy life expectancy',
    'Freedom to make life choices',
    'Generosity',
    'Perceptions of corruption',
]

# Hangi metrikler ters normalize edilecek (yuksek = kotu)
INVERSE_METRICS = ['Perceptions of corruption']


# Preset karar profilleri - her metrige verilen agirlik (toplam = 1.0)
PROFILES = {
    'Student': {
        'GDP per capita': 0.15,
        'Social support': 0.25,
        'Healthy life expectancy': 0.10,
        'Freedom to make life choices': 0.25,
        'Generosity': 0.10,
        'Perceptions of corruption': 0.15,
    },
    'Retiree': {
        'GDP per capita': 0.15,
        'Social support': 0.20,
        'Healthy life expectancy': 0.30,
        'Freedom to make life choices': 0.05,
        'Generosity': 0.05,
        'Perceptions of corruption': 0.25,
    },
    'Family': {
        'GDP per capita': 0.20,
        'Social support': 0.25,
        'Healthy life expectancy': 0.20,
        'Freedom to make life choices': 0.15,
        'Generosity': 0.05,
        'Perceptions of corruption': 0.15,
    },
    'Entrepreneur': {
        'GDP per capita': 0.30,
        'Social support': 0.10,
        'Healthy life expectancy': 0.10,
        'Freedom to make life choices': 0.25,
        'Generosity': 0.05,
        'Perceptions of corruption': 0.20,
    },
    'Balanced': {
        'GDP per capita': 1/6,
        'Social support': 1/6,
        'Healthy life expectancy': 1/6,
        'Freedom to make life choices': 1/6,
        'Generosity': 1/6,
        'Perceptions of corruption': 1/6,
    },
}


# Profil aciklamalari (UI icin)
PROFILE_DESCRIPTIONS = {
    'Student': 'Ozgurluk ve sosyal destek on planda - yurt disi egitim icin ideal.',
    'Retiree': 'Saglik ve dusuk yolsuzluk kritik - huzurlu yaslilik.',
    'Family': 'Sosyal destek ve saglik dengeli - cocuk buyutmek icin.',
    'Entrepreneur': 'Ekonomik guc ve ozgurluk - is kurmak icin.',
    'Balanced': 'Tum metrikler esit agirlik - referans baseline.',
}


# Kume bilgileri (Faz 3 sonuclarindan)
CLUSTER_NAMES = {
    0: 'Pragmatic Middle',
    1: 'Fragile States',
    2: 'Established Prosperity',
    3: 'Generous Emergers',
}

CLUSTER_NAMES_TR = {
    0: 'Pragmatik Orta',
    1: 'Kirilgan Devletler',
    2: 'Refah Zirvesi',
    3: 'Comert Yukselenler',
}

CLUSTER_COLORS = {
    0: '#e74c3c',
    1: '#3498db',
    2: '#2ecc71',
    3: '#f39c12',
}
