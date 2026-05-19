import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from config import COLORS, CURRENCY_INFO, CURRENCY_COLS, CHART_COLORS
from helpers import kpi_card, chart_container, base_layout, format_rp, calc_period_return, calc_cumulative_pct, page_header


def render(df_fx, start_year, end_year):
    page_header("Exchange Rates", "Analisis Nilai Tukar Rupiah terhadap Mata Uang Dunia")

    options = {f"{CURRENCY_INFO[c]['flag']} {CURRENCY_INFO[c]['code']} - {CURRENCY_INFO[c]['name']}": c for c in CURRENCY_COLS}
    selected_label = st.selectbox("Pilih Mata Uang", list(options.keys()),
                                  index=list(options.keys()).index("🇺🇸 USD - Dolar Amerika Serikat"))
    selected = options[selected_label]
    info = CURRENCY_INFO[selected]

    cur_year = df_fx['Tanggal'].dt.year.max()
    ytd = df_fx[df_fx['Tanggal'].dt.year == cur_year]

    latest = df_fx[selected].iloc[-1]
    ytd_ret = calc_period_return(ytd[selected])
    highest = df_fx[selected].max()
    lowest = df_fx[selected].min()

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Nilai Tukar Terakhir", format_rp(latest), subtitle=f"{info['code']}/IDR")
    with cols[1]:
        kpi_card("Perubahan YTD", f"{ytd_ret:+.2f}%", delta=ytd_ret, delta_suffix='%')
    with cols[2]:
        kpi_card("Tertinggi (Periode)", format_rp(highest),
                 subtitle=df_fx.loc[df_fx[selected].idxmax(), 'Tanggal'].strftime('%d %b %Y'))
    with cols[3]:
        kpi_card("Terendah (Periode)", format_rp(lowest),
                 subtitle=df_fx.loc[df_fx[selected].idxmin(), 'Tanggal'].strftime('%d %b %Y'))

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart 1: Simple line
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_fx['Tanggal'], y=df_fx[selected], name=f"{info['code']}/IDR",
                              line=dict(color=COLORS['primary'], width=2),
                              fill='tozeroy', fillcolor='rgba(26,35,50,0.06)',
                              hovertemplate="%{x|%d %b %Y}<br>" + format_rp(0).replace('0', '') + "%{y:,.0f}<extra></extra>"))
    fig1.update_layout(**base_layout(f"Pergerakan {info['code']}/IDR", height=420))
    fig1.update_yaxes(title_text="Nilai Tukar (IDR)")

    # Chart 2: Monthly returns grouped bar
    df_m = df_fx[['Tanggal', selected]].copy()
    df_m['Year'] = df_m['Tanggal'].dt.year
    df_m['Month'] = df_m['Tanggal'].dt.month
    monthly_rows = []
    months_id = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']
    for y in sorted(df_m['Year'].unique()):
        for m in range(1, 13):
            md = df_m[(df_m['Year'] == y) & (df_m['Month'] == m)]
            if len(md) >= 2:
                ret = calc_period_return(md[selected])
                monthly_rows.append({'Bulan': months_id[m-1], 'Tahun': str(y), 'Return (%)': ret, 'month_num': m})
    if monthly_rows:
        mon_df = pd.DataFrame(monthly_rows).sort_values('month_num')
        fig2 = px.bar(mon_df, x='Bulan', y='Return (%)', color='Tahun', barmode='group',
                      color_discrete_sequence=CHART_COLORS, text_auto='.1f',
                      category_orders={'Bulan': months_id})
        fig2.update_layout(**base_layout(f"Return Bulanan {info['code']}/IDR", height=420))
        fig2.update_yaxes(ticksuffix="%")
        fig2.update_traces(textposition='outside', textfont_size=8)
    else:
        fig2 = go.Figure()
        fig2.update_layout(**base_layout("Return Bulanan - Data tidak cukup"))

    c1, c2 = st.columns(2)
    with c1:
        chart_container(fig1)
    with c2:
        chart_container(fig2)

    # Chart 3: Histogram
    daily_ret = df_fx[selected].pct_change().dropna() * 100
    fig3 = go.Figure(go.Histogram(x=daily_ret, nbinsx=50, marker_color=COLORS['primary'],
                                   opacity=0.85, hovertemplate="Range: %{x:.2f}%<br>Count: %{y}<extra></extra>"))
    mean_r = daily_ret.mean()
    std_r = daily_ret.std()
    fig3.add_vline(x=mean_r, line_dash="dash", line_color=COLORS['accent'], line_width=2)
    fig3.update_layout(**base_layout(f"Distribusi Perubahan Harian {info['code']}/IDR", height=400, showlegend=False))
    fig3.update_xaxes(title_text="% Perubahan Harian", ticksuffix="%")
    fig3.update_yaxes(title_text="Frekuensi")
    fig3.update_layout(annotations=[dict(
        text=f"<b>Mean:</b> {mean_r:.4f}%<br><b>Std:</b> {std_r:.4f}%", xref="paper", yref="paper",
        x=0.97, y=0.95, showarrow=False, align="right", font=dict(size=11, color=COLORS['text']),
        bgcolor="rgba(255,255,255,0.9)", bordercolor=COLORS['card_border'], borderwidth=1, borderpad=8
    )])

    # Chart 4: Comparison cumulative %
    cum = calc_cumulative_pct(df_fx, 'Tanggal', CURRENCY_COLS)
    fig4 = go.Figure()
    for i, c in enumerate(CURRENCY_COLS):
        ci = CURRENCY_INFO[c]
        is_selected = (c == selected)
        fig4.add_trace(go.Scatter(
            x=cum['Tanggal'], y=cum[c], name=f"{ci['code']}",
            line=dict(color=COLORS['accent'] if is_selected else '#ccc', width=3 if is_selected else 1),
            opacity=1 if is_selected else 0.4,
            hovertemplate=f"{ci['code']}: " + "%{y:.2f}%<extra></extra>"
        ))
    fig4.update_layout(**base_layout(f"Perbandingan {info['code']} dengan Mata Uang Lain", height=400))
    fig4.update_yaxes(title_text="% Perubahan Kumulatif", ticksuffix="%")

    c3, c4 = st.columns(2)
    with c3:
        chart_container(fig3)
    with c4:
        chart_container(fig4)
