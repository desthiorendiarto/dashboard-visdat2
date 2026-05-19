import streamlit as st
from helpers import inject_css, load_data, filter_data
import tab2_detail_fx
import tab3_ringkasan_ihsg
import tab4_detail_sektor

st.set_page_config(
    page_title="Dashboard Ekonomi Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

df_idx_raw, df_fx_raw = load_data()

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.5rem 0;">
        <div style="font-size:1.1rem; font-weight:700; letter-spacing:0.5px; line-height:1.4;">
            Dashboard Ekonomi Indonesia
        </div>
        <div style="font-size:0.75rem; color:#CBDFDE; font-weight:400; margin-top:2px;">
            Kurs Rupiah & IHSG
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["Exchange Rates", "Market Overview", "Sector Analysis"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    all_years = sorted(df_idx_raw['time'].dt.year.unique())
    st.markdown("##### Filter")
    year_range = st.slider("Periode", min_value=int(all_years[0]), max_value=int(all_years[-1]),
                           value=(int(all_years[0]), int(all_years[-1])))

    st.markdown("---")

    with st.expander("Tentang Dashboard"):
        st.markdown("""
        Dashboard ini menganalisis hubungan antara **Nilai Tukar Rupiah** terhadap 10 mata uang utama
        dunia dan **Kinerja Sektor Pasar Saham Indonesia** (IHSG).

        **Periode Data:** Jan 2021 - Mei 2026
        """)

    with st.expander("Sumber Data"):
        st.markdown("""
        - **Yahoo Finance**
        - **Bank Indonesia**
        - **IDX (Indonesia Stock Exchange)**
        """)

    last_date = df_idx_raw['time'].iloc[-1].strftime('%d %B %Y')
    st.markdown(f"<div style='text-align:center;font-size:0.72rem;color:#CBDFDE;margin-top:1.5rem;'>Update terakhir: {last_date}</div>", unsafe_allow_html=True)

df_idx = filter_data(df_idx_raw, 'time', year_range[0], year_range[1])
df_fx = filter_data(df_fx_raw, 'Tanggal', year_range[0], year_range[1])

if page == "Exchange Rates":
    tab2_detail_fx.render(df_fx, year_range[0], year_range[1])
elif page == "Market Overview":
    tab3_ringkasan_ihsg.render(df_idx, df_fx, year_range[0], year_range[1])
elif page == "Sector Analysis":
    tab4_detail_sektor.render(df_idx, df_fx, year_range[0], year_range[1])
