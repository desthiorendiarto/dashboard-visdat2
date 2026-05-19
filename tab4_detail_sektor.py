import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from config import COLORS, SECTOR_NAMES, SECTOR_COLS, CHART_COLORS
from helpers import kpi_card, chart_container, base_layout, calc_period_return, calc_cumulative_pct, page_header


def render(df_idx, df_fx, start_year, end_year):
    page_header("Sector Analysis", "Analisis Mendalam per Sektor & Korelasinya dengan USD/IDR")

    options = {SECTOR_NAMES[s]: s for s in SECTOR_COLS}
    selected_name = st.selectbox("Pilih Sektor", list(options.keys()))
    selected = options[selected_name]

    cur_year = df_idx['time'].dt.year.max()
    ytd = df_idx[df_idx['time'].dt.year == cur_year]

    latest = df_idx[selected].iloc[-1]
    ytd_ret = calc_period_return(ytd[selected])
    highest = df_idx[selected].max()
    lowest = df_idx[selected].min()

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Nilai Indeks Terakhir", f"{latest:,.2f}", subtitle=selected_name)
    with cols[1]:
        kpi_card("Return YTD", f"{ytd_ret:+.2f}%", delta=ytd_ret, delta_suffix='%')
    with cols[2]:
        kpi_card("Tertinggi (Periode)", f"{highest:,.2f}",
                 subtitle=df_idx.loc[df_idx[selected].idxmax(), 'time'].strftime('%d %b %Y'))
    with cols[3]:
        kpi_card("Terendah (Periode)", f"{lowest:,.2f}",
                 subtitle=df_idx.loc[df_idx[selected].idxmin(), 'time'].strftime('%d %b %Y'))

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart 1: Simple line (no MA, no range selector)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_idx['time'], y=df_idx[selected], name=selected_name,
                              line=dict(color=COLORS['primary'], width=2),
                              fill='tozeroy', fillcolor='rgba(66,92,89,0.08)',
                              hovertemplate=f"{selected_name}: " + "%{y:,.2f}<extra></extra>"))
    fig1.update_layout(**base_layout(f"Pergerakan Indeks {selected_name}", height=430))
    fig1.update_yaxes(title_text="Nilai Indeks")

    # Chart 2: Monthly returns grouped bar
    df_m = df_idx[['time', selected]].copy()
    df_m['Year'] = df_m['time'].dt.year
    df_m['Month'] = df_m['time'].dt.month
    months_id = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']
    monthly_rows = []
    for y in sorted(df_m['Year'].unique()):
        for m in range(1, 13):
            md = df_m[(df_m['Year'] == y) & (df_m['Month'] == m)]
            if len(md) >= 2:
                ret = calc_period_return(md[selected])
                monthly_rows.append({'Bulan': months_id[m-1], 'Tahun': str(y), 'Return (%)': ret, 'mn': m})
    if monthly_rows:
        mon_df = pd.DataFrame(monthly_rows).sort_values('mn')
        fig2 = px.bar(mon_df, x='Bulan', y='Return (%)', color='Tahun', barmode='group',
                      color_discrete_sequence=CHART_COLORS, text_auto='.1f',
                      category_orders={'Bulan': months_id})
        fig2.update_layout(**base_layout(f"Return Bulanan {selected_name}", height=430))
        fig2.update_yaxes(ticksuffix="%")
        fig2.update_traces(textposition='outside', textfont_size=8)
    else:
        fig2 = go.Figure()
        fig2.update_layout(**base_layout("Data tidak cukup"))

    c1, c2 = st.columns(2)
    with c1:
        chart_container(fig1)
    with c2:
        chart_container(fig2)

    # Chart 3: Histogram
    daily_ret = df_idx[selected].pct_change().dropna() * 100
    fig3 = go.Figure(go.Histogram(x=daily_ret, nbinsx=50, marker_color=COLORS['primary'], opacity=0.85))
    mean_r, med_r = daily_ret.mean(), daily_ret.median()
    fig3.add_vline(x=mean_r, line_dash="dash", line_color=COLORS['accent'], line_width=2)
    fig3.add_vline(x=med_r, line_dash="dot", line_color=COLORS['green'], line_width=2)
    fig3.update_layout(**base_layout(f"Distribusi Return Harian {selected_name}", height=420, showlegend=False))
    fig3.update_xaxes(title_text="% Return Harian", ticksuffix="%")
    fig3.update_yaxes(title_text="Frekuensi")
    fig3.update_layout(annotations=[
        dict(text=f"<b>Mean:</b> {mean_r:.4f}%<br><b>Median:</b> {med_r:.4f}%",
             xref="paper", yref="paper", x=0.97, y=0.95, showarrow=False, align="right",
             font=dict(size=11, color=COLORS['text']),
             bgcolor="rgba(255,255,255,0.9)", bordercolor=COLORS['card_border'], borderwidth=1, borderpad=8)
    ])

    # Chart 4: Scatter vs USD/IDR
    sec_ret = df_idx[selected].pct_change().dropna() * 100
    usd_ret = df_fx['USDIDR'].pct_change().dropna() * 100
    min_len = min(len(sec_ret), len(usd_ret))
    scatter_df = pd.DataFrame({
        'Return Sektor (%)': sec_ret.iloc[:min_len].values,
        'Return USD/IDR (%)': usd_ret.iloc[:min_len].values
    })
    corr_val = scatter_df['Return Sektor (%)'].corr(scatter_df['Return USD/IDR (%)'])
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=scatter_df['Return Sektor (%)'], y=scatter_df['Return USD/IDR (%)'],
        mode='markers', marker=dict(color=COLORS['primary'], opacity=0.35, size=5),
        hovertemplate="Sektor: %{x:.2f}%<br>USD/IDR: %{y:.2f}%<extra></extra>"
    ))
    x_vals = scatter_df['Return Sektor (%)'].values
    y_vals = scatter_df['Return USD/IDR (%)'].values
    mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
    z = np.polyfit(x_vals[mask], y_vals[mask], 1)
    x_line = np.linspace(x_vals[mask].min(), x_vals[mask].max(), 100)
    y_line = np.poly1d(z)(x_line)
    fig4.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                              line=dict(color=COLORS['accent'], width=2.5), name='Trendline'))
    fig4.update_layout(**base_layout(f"Korelasi {selected_name} vs USD/IDR", height=420, showlegend=False))
    fig4.update_layout(annotations=[dict(
        text=f"r = {corr_val:.4f}", xref="paper", yref="paper",
        x=0.95, y=0.95, showarrow=False, font=dict(size=13, color=COLORS['accent'], family='Inter'),
        bgcolor="white", bordercolor=COLORS['accent'], borderwidth=2, borderpad=8
    )])
    fig4.update_xaxes(ticksuffix="%")
    fig4.update_yaxes(ticksuffix="%")

    c3, c4 = st.columns(2)
    with c3:
        chart_container(fig3)
    with c4:
        chart_container(fig4)

    # Chart 5: Drawdown (full width)
    prices = df_idx[selected]
    running_max = prices.cummax()
    drawdown = ((prices - running_max) / running_max) * 100
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=df_idx['time'], y=drawdown, fill='tozeroy', name='Drawdown',
        line=dict(color=COLORS['red'], width=1), fillcolor='rgba(231,76,60,0.3)',
        hovertemplate="%{x|%d %b %Y}<br>Drawdown: %{y:.2f}%<extra></extra>"
    ))
    max_dd = drawdown.min()
    max_dd_date = df_idx.loc[drawdown.idxmin(), 'time']
    fig5.add_annotation(x=max_dd_date, y=max_dd, text=f"Max: {max_dd:.1f}%",
                        showarrow=True, arrowhead=2, arrowcolor=COLORS['red'],
                        font=dict(color=COLORS['red'], size=11))
    fig5.update_layout(**base_layout(f"Drawdown {selected_name} (Penurunan dari Puncak)", height=350, showlegend=False))
    fig5.update_yaxes(title_text="Drawdown (%)", ticksuffix="%")
    chart_container(fig5)
