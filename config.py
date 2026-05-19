# ============================================================
# Configuration & Constants
# ============================================================

COLORS = {
    'primary': '#1a2332',      # Dark navy - headers, text
    'secondary': '#2d3748',    # Medium dark - subtitles
    'accent': '#c9943e',       # Gold accent - highlights
    'sidebar': '#1e293b',      # Dark sidebar
    'sidebar_hover': '#334155',
    'light_bg': '#f0f2f5',     # Light gray background
    'card_border': '#e2e8f0',  # Subtle card borders
    'white': '#FFFFFF',
    'red': '#dc2626',          # Negative
    'green': '#16a34a',        # Positive
    'text': '#374151',         # Readable dark gray for axes
    'text_light': '#6b7280',   # Secondary text
}

SECTOR_NAMES = {
    'idxbasic': 'Basic Materials',
    'idxnoncyc': 'Non-Cyclical Consumer',
    'idxhealth': 'Healthcare',
    'idxpropert': 'Property & Real Estate',
    'idxtechno': 'Technology',
    'idxtrans': 'Transportation & Logistic',
    'idxindust': 'Industrials',
    'idxfinance': 'Financials',
    'idxenergy': 'Energy',
    'idxinfra': 'Infrastructure',
    'idxcyclic': 'Consumer Cyclical',
}

SECTOR_COLS = list(SECTOR_NAMES.keys())

CURRENCY_INFO = {
    'AUDIDR': {'code': 'AUD', 'name': 'Dolar Australia', 'flag': '🇦🇺'},
    'CADIDR': {'code': 'CAD', 'name': 'Dolar Kanada', 'flag': '🇨🇦'},
    'CHFIDR': {'code': 'CHF', 'name': 'Franc Swiss', 'flag': '🇨🇭'},
    'CNHIDR': {'code': 'CNH', 'name': 'Yuan Tiongkok', 'flag': '🇨🇳'},
    'EURIDR': {'code': 'EUR', 'name': 'Euro', 'flag': '🇪🇺'},
    'GBPIDR': {'code': 'GBP', 'name': 'Poundsterling Inggris', 'flag': '🇬🇧'},
    'HKDIDR': {'code': 'HKD', 'name': 'Dolar Hong Kong', 'flag': '🇭🇰'},
    'JPYIDR': {'code': 'JPY', 'name': 'Yen Jepang', 'flag': '🇯🇵'},
    'NZDIDR': {'code': 'NZD', 'name': 'Dolar Selandia Baru', 'flag': '🇳🇿'},
    'USDIDR': {'code': 'USD', 'name': 'Dolar Amerika Serikat', 'flag': '🇺🇸'},
}

CURRENCY_COLS = list(CURRENCY_INFO.keys())

CHART_COLORS = [
    '#1a2332', '#c9943e', '#dc2626', '#16a34a', '#2563eb',
    '#7c3aed', '#ea580c', '#0891b2', '#4b5563', '#db2777', '#06b6d4'
]
