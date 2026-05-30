import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="FuelCRM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# GLOBAL CSS (UI SaaS STYLE)
# =========================
st.markdown("""
<style>

/* ========== MAIN ========== */
.block-container {
    padding: 1.5rem 2rem;
    background-color: #f6f7fb;
}

/* ========== SIDEBAR ========== */
[data-testid="stSidebar"] {
    background-color: #0f172a;
}

[data-testid="stSidebar"] * {
    color: white;
    font-weight: 500;
}

/* logo/title */
.sidebar-title {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 20px;
}

/* menu item */
.menu-item {
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    cursor: pointer;
}

/* highlight dashboard */
.active {
    background: #f59e0b;
    color: black !important;
    font-weight: 700;
}

/* ========== TOP HEADER ========== */
.header-title {
    font-size: 28px;
    font-weight: 800;
}

.subtext {
    color: #6b7280;
    margin-top: -8px;
}

/* ========== KPI CARDS ========== */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 18px 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.kpi-title {
    font-size: 14px;
    color: #6b7280;
}

.kpi-value {
    font-size: 22px;
    font-weight: 800;
}

/* icon box */
.icon-box {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

/* ========== CLIENT BOX ========== */
.empty-box {
    background: white;
    border-radius: 16px;
    padding: 60px;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("## ⛽ FuelCRM")

    st.markdown("### Menu")

    st.markdown('<div class="menu-item active">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">👤 Clienti</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">➕ Nuovo Cliente</div>', unsafe_allow_html=True)

    st.write("")
    if st.button("🚪 Esci"):
        st.stop()


# =========================
# HEADER
# =========================
st.markdown('<div class="header-title">Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Gestione prezzi e invio offerte</div>', unsafe_allow_html=True)


# =========================
# TOP BAR (INPUT + BUTTON)
# =========================
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    pass

with col2:
    prezzo = st.text_input("Prezzo Base (€/L)", "1.0000")

with col3:
    st.write("")
    st.button("📩 Invia a Tutti")


st.write("---")


# =========================
# KPI ROW
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="kpi-card">
        <div>
            <div class="kpi-title">Clienti</div>
            <div class="kpi-value">0</div>
        </div>
        <div class="icon-box" style="background:#e0e7ff;">👤</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="kpi-card">
        <div>
            <div class="kpi-title">Margine Medio</div>
            <div class="kpi-value">€0.0000/L</div>
        </div>
        <div class="icon-box" style="background:#ffedd5;">📈</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="kpi-card">
        <div>
            <div class="kpi-title">Prezzo Medio</div>
            <div class="kpi-value">€0.0000/L</div>
        </div>
        <div class="icon-box" style="background:#dcfce7;">💲</div>
    </div>
    """, unsafe_allow_html=True)


st.write("---")


# =========================
# CLIENT SECTION
# =========================
st.markdown("### Clienti (0)")

st.markdown("""
<div class="empty-box">
    <div style="font-size:40px;">⛽</div>
    <h3>Nessun cliente ancora</h3>
    <p style="color:#6b7280;">
        Aggiungi il primo cliente per iniziare a gestire le offerte.
    </p>
</div>
""", unsafe_allow_html=True)
