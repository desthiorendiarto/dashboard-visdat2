import streamlit as st
import pandas as pd
import numpy as np
from config import COLORS


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #f0f2f5;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #1a2332 100%);
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 0.25rem; }
    [data-testid="stSidebar"] .stRadio > div > label {
        background-color: rgba(255,255,255,0.06);
        padding: 0.65rem 1.1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 1px 0;
        font-weight: 500;
        font-size: 0.9rem;
        border: 1px solid transparent;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: rgba(255,255,255,0.12);
        border-color: rgba(201,148,62,0.3);
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background-color: #c9943e;
        border-color: #c9943e;
        font-weight: 600;
        color: #1a2332 !important;
    }
    [data-testid="stSidebar"] .stSlider label { color: #94a3b8 !important; font-size: 0.82rem; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08); margin: 0.8rem 0; }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        font-size: 0.82rem; font-weight: 500;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        border-top: 3px solid #c9943e;
        min-height: 110px;
        text-align: center;
    }
    .kpi-label {
        font-size: 0.68rem; color: #6b7280; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 1.4rem; font-weight: 700; color: #1a2332;
        line-height: 1.2; margin-bottom: 0.15rem;
    }
    .kpi-delta-pos { color: #16a34a; font-size: 0.82rem; font-weight: 600; }
    .kpi-delta-neg { color: #dc2626; font-size: 0.82rem; font-weight: 600; }
    .kpi-sub { font-size: 0.68rem; color: #9ca3af; margin-top: 0.15rem; }

    /* Page header */
    .page-header {
        background: linear-gradient(135deg, #1e293b 0%, #1a2332 100%);
        border-radius: 12px;
        padding: 1.4rem 2rem;
        margin-bottom: 1.2rem;
        color: white;
        box-shadow: 0 4px 16px rgba(26,35,50,0.2);
    }
    .page-header h2 {
        margin: 0; font-size: 1.45rem; font-weight: 700; color: white !important;
    }
    .page-header p {
        margin: 0.3rem 0 0 0; font-size: 0.85rem; color: #94a3b8; font-weight: 400;
    }

    /* Chart containers */
    .chart-box {
        background: white;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }

    /* Selectbox styling */
    .stSelectbox label { color: #1a2332 !important; font-weight: 600 !important; font-size: 0.85rem; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    div[data-testid="stExpander"] { border: none !important; background: transparent !important; }
    .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, delta=None, delta_suffix='', subtitle=''):
    delta_html = ''
    if delta is not None:
        arrow = '▲' if delta >= 0 else '▼'
        cls = 'kpi-delta-pos' if delta >= 0 else 'kpi-delta-neg'
        delta_html = f'<div class="{cls}">{arrow} {abs(delta):.2f}{delta_suffix}</div>'
    sub_html = f'<div class="kpi-sub">{subtitle}</div>' if subtitle else ''
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>{delta_html}{sub_html}
    </div>""", unsafe_allow_html=True)


def chart_container(fig):
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


def base_layout(title='', height=420, showlegend=True):
    return dict(
        title=dict(text=f"<b>{title}</b>", font=dict(size=14, color=COLORS['primary'], family='Inter'), x=0.5, xanchor='center'),
        height=height, plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', color='#111827', size=12),
        margin=dict(l=70, r=30, t=55, b=55),
        showlegend=showlegend,
        legend=dict(bgcolor='rgba(255,255,255,0.95)', bordercolor=COLORS['card_border'], borderwidth=1, font=dict(size=10, color='#111827')),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color='#111827', size=11),
                   title_font=dict(color='#111827', size=12, family='Inter'),
                   title_standoff=15),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color='#111827', size=11),
                   title_font=dict(color='#111827', size=12, family='Inter'),
                   title_standoff=15),
    )


def format_rp(val, decimals=0):
    if decimals == 0:
        return f"Rp{val:,.0f}"
    return f"Rp{val:,.{decimals}f}"


@st.cache_data
def load_data():
    df_idx = pd.read_excel('Data Dashboard Visdat.xlsx', sheet_name='IDX SECTOR')
    df_fx = pd.read_excel('Data Dashboard Visdat.xlsx', sheet_name='NILAI TUKAR')
    if 'idxtechno.1' in df_idx.columns:
        df_idx = df_idx.drop(columns=['idxtechno.1'])
    return df_idx, df_fx


def filter_data(df, date_col, start_year, end_year):
    return df[(df[date_col].dt.year >= start_year) & (df[date_col].dt.year <= end_year)].copy()


def calc_period_return(series):
    if len(series) < 2:
        return 0
    return ((series.iloc[-1] / series.iloc[0]) - 1) * 100


def calc_cumulative_pct(df, date_col, cols):
    result = pd.DataFrame({date_col: df[date_col]})
    for c in cols:
        result[c] = ((df[c] / df[c].iloc[0]) - 1) * 100
    return result


def calc_yearly_returns(df, date_col, cols, name_map):
    years = sorted(df[date_col].dt.year.unique())
    rows = []
    for y in years:
        yd = df[df[date_col].dt.year == y]
        if len(yd) < 2:
            continue
        for c in cols:
            ret = calc_period_return(yd[c])
            rows.append({'Tahun': str(y), 'Nama': name_map.get(c, c), 'Return (%)': ret, 'col': c})
    return pd.DataFrame(rows)
