import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from config import COLORS, SECTOR_NAMES, SECTOR_COLS, CURRENCY_COLS, CHART_COLORS
from helpers import kpi_card, chart_container, base_layout, calc_period_return, calc_cumulative_pct, calc_yearly_returns, page_header


def render(df_idx, df_fx, start_year, end_year):
    page_header("Market Overview", "Kinerja Sektor Pasar Saham Indonesia & Hubungannya dengan USD/IDR")

    cur_year = df_idx['time'].dt.year.max()
    ytd_idx = df_idx[df_idx['time'].dt.year == cur_year]
    ytd_fx = df_fx[df_fx['Tanggal'].dt.year == cur_year]

    ihsg_ret = calc_period_return(ytd_idx['composite'])
    usd_ret = calc_period_return(ytd_fx['USDIDR'])

    sector_ytd = {s: calc_period_return(ytd_idx[s]) for s in SECTOR_COLS}
    best_s = max(sector_ytd, key=sector_ytd.get)
    worst_s = min(sector_ytd, key=sector_ytd.get)

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Return IHSG (YTD)", f"{ihsg_ret:+.2f}%", delta=ihsg_ret, delta_suffix='%',
                 subtitle=f"IHSG: {df_idx['composite'].iloc[-1]:,.0f}")
    with cols[1]:
        kpi_card("Return USD/IDR (YTD)", f"{usd_ret:+.2f}%", delta=usd_ret, delta_suffix='%',
                 subtitle=f"Rp{df_fx['USDIDR'].iloc[-1]:,.0f}")
    with cols[2]:
        kpi_card("Sektor Terbaik (YTD)", SECTOR_NAMES[best_s],
                 delta=sector_ytd[best_s], delta_suffix='%')
    with cols[3]:
        kpi_card("Sektor Terburuk (YTD)", SECTOR_NAMES[worst_s],
                 delta=sector_ytd[worst_s], delta_suffix='%')

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart 1: IHSG vs USD/IDR dual axis
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=df_idx['time'], y=df_idx['composite'], name='IHSG',
                              line=dict(color=COLORS['primary'], width=2),
                              hovertemplate="IHSG: %{y:,.0f}<extra></extra>"), secondary_y=False)
    fig1.add_trace(go.Scatter(x=df_fx['Tanggal'], y=df_fx['USDIDR'], name='USD/IDR',
                              line=dict(color=COLORS['accent'], width=2),
                              hovertemplate="USD/IDR: Rp%{y:,.0f}<extra></extra>"), secondary_y=True)
    layout = base_layout("Pergerakan IHSG vs USD/IDR", height=440)
    fig1.update_layout(**layout)
    fig1.update_yaxes(title_text="IHSG", secondary_y=False, showgrid=False)
    fig1.update_yaxes(title_text="USD/IDR (Rp)", secondary_y=True, showgrid=False)

    # Chart 2: Sector YTD returns bar
    ytd_df = pd.DataFrame([
        {'Sektor': SECTOR_NAMES[s], 'Return (%)': sector_ytd[s]} for s in SECTOR_COLS
    ]).sort_values('Return (%)', ascending=True)
    bar_colors = [COLORS['accent'] if r > 0 else COLORS['red'] for r in ytd_df['Return (%)']]
    fig2 = go.Figure(go.Bar(
        x=ytd_df['Return (%)'], y=ytd_df['Sektor'], orientation='h',
        marker_color=bar_colors, text=[f"{v:+.2f}%" for v in ytd_df['Return (%)']],
        textposition='outside', hovertemplate="%{y}: %{x:.2f}%<extra></extra>"
    ))
    fig2.update_layout(**base_layout(f"Return Sektor YTD ({cur_year})", height=440, showlegend=False))
    fig2.update_xaxes(title_text="% Return", ticksuffix="%")

    c1, c2 = st.columns(2)
    with c1:
        chart_container(fig1)
    with c2:
        chart_container(fig2)

    # Chart 3: Correlation sector vs USD/IDR
    corr_data = []
    usd_ret_series = df_fx['USDIDR'].pct_change()
    for s in SECTOR_COLS:
        sec_ret = df_idx[s].pct_change()
        min_len = min(len(sec_ret), len(usd_ret_series))
        corr = sec_ret.iloc[:min_len].corr(usd_ret_series.iloc[:min_len])
        corr_data.append({'Sektor': SECTOR_NAMES[s], 'Korelasi': corr})
    corr_df = pd.DataFrame(corr_data).sort_values('Korelasi', ascending=True)
    corr_colors = [COLORS['red'] if c < 0 else COLORS['green'] for c in corr_df['Korelasi']]
    fig3 = go.Figure(go.Bar(
        x=corr_df['Korelasi'], y=corr_df['Sektor'], orientation='h',
        marker_color=corr_colors, text=[f"{v:.3f}" for v in corr_df['Korelasi']],
        textposition='outside', hovertemplate="%{y}: %{x:.4f}<extra></extra>"
    ))
    fig3.update_layout(**base_layout("Korelasi Return Sektor vs USD/IDR", height=440, showlegend=False))
    fig3.update_xaxes(title_text="Koefisien Korelasi")
    fig3.update_layout(annotations=[dict(
        text="Negatif = saat USD menguat, sektor cenderung turun", xref="paper", yref="paper",
        x=0.5, y=-0.12, showarrow=False, font=dict(size=10, color='#888')
    )])

    # Chart 4: All sectors cumulative %
    cum = calc_cumulative_pct(df_idx, 'time', SECTOR_COLS + ['composite'])
    fig4 = go.Figure()
    for i, s in enumerate(SECTOR_COLS):
        fig4.add_trace(go.Scatter(
            x=cum['time'], y=cum[s], name=SECTOR_NAMES[s],
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1.5),
            hovertemplate=f"{SECTOR_NAMES[s]}: " + "%{y:.2f}%<extra></extra>"
        ))
    fig4.add_trace(go.Scatter(
        x=cum['time'], y=cum['composite'], name='IHSG (Composite)',
        line=dict(color='black', width=3, dash='dash'),
        hovertemplate="IHSG: %{y:.2f}%<extra></extra>"
    ))
    fig4.update_layout(**base_layout("Pergerakan Semua Sektor (% Perubahan Kumulatif)", height=440))
    fig4.update_yaxes(title_text="% Perubahan", ticksuffix="%")

    c3, c4 = st.columns(2)
    with c3:
        chart_container(fig3)
    with c4:
        chart_container(fig4)

    # Chart 5: Yearly returns grouped bar (full width)
    name_map = {s: SECTOR_NAMES[s] for s in SECTOR_COLS}
    yr_df = calc_yearly_returns(df_idx, 'time', SECTOR_COLS, name_map)
    fig5 = px.bar(yr_df, x='Nama', y='Return (%)', color='Tahun', barmode='group',
                  color_discrete_sequence=CHART_COLORS, text_auto='.1f')
    fig5.update_layout(**base_layout("Return Sektor per Tahun", height=450))
    fig5.update_xaxes(title_text="", tickangle=-35)
    fig5.update_yaxes(ticksuffix="%")
    fig5.update_traces(textposition='outside', textfont_size=8)
    chart_container(fig5)
