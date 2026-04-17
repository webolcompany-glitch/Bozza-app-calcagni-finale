import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="Fuel SaaS", layout="wide")

# =========================
# 🏢 AZIENDA
# =========================
azienda = st.query_params.get("azienda", "demo")
if isinstance(azienda, list):
    azienda = azienda[0]

FILE = f"clienti_{azienda}.csv"

st.markdown(f"## 🏢 Azienda: {azienda.upper()}")

# =========================
# 📧 EMAIL
# =========================
EMAIL_MITTENTE = "webolcompany@gmail.com"
PASSWORD_APP = "neqr ewtb bdkr lmca"

def invia_email(destinatario, prezzo, template, nome=""):
    try:
        data = datetime.now().strftime("%d/%m/%Y")

        testo = template\
            .replace("{prezzo}", f"{prezzo:.3f}")\
            .replace("{nome}", nome)\
            .replace("{data}", data)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"OFFERTA CARBURANTE - {data}"
        msg["From"] = EMAIL_MITTENTE
        msg["To"] = destinatario

        msg.attach(MIMEText(testo, "html", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_MITTENTE, PASSWORD_APP)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        st.error(f"Errore email: {e}")

# =========================
# 🔒 UTIL
# =========================
def format_euro(x):
    if x is None or pd.isna(x):
        return "0,000"
    return f"{round(float(x), 3):.3f}".replace(".", ",")

def calc_price(base, margine, trasporto):
    return round(float(base) + float(margine) + float(trasporto), 3)

def filtra_clienti(df, search):
    if not search:
        return df
    return df[
        df["Nome"].astype(str).str.contains(search, case=False, na=False) |
        df["PIVA"].astype(str).str.contains(search, case=False, na=False) |
        df["Telefono"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# 💾 DATA
# =========================
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        for col in ["Nome","PIVA","Telefono","Email"]:
            df[col] = df[col].astype(str)

        for col in ["Margine","Trasporto"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        if "UltimoPrezzo" not in df.columns:
            df["UltimoPrezzo"] = None

        return df

    return pd.DataFrame(columns=[
        "ID","Nome","PIVA","Telefono","Email",
        "Margine","Trasporto","UltimoPrezzo"
    ])

def save_data(df):
    df.to_csv(FILE, index=False)

# =========================
# INIT
# =========================
if "clienti" not in st.session_state:
    st.session_state.clienti = load_data()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "prezzo_base" not in st.session_state:
    st.session_state.prezzo_base = 1.000

if "email_template" not in st.session_state:
    st.session_state.email_template = "Gentile cliente,<br><br>{prezzo}"

if "whatsapp_template" not in st.session_state:
    st.session_state.whatsapp_template = "Prezzo oggi: {prezzo} €/L - {nome} ({data})"

df = st.session_state.clienti

# =========================
# NAV
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"

with c2:
    if st.button("👤 Clienti", use_container_width=True):
        st.session_state.page = "clienti"

with c3:
    if st.button("➕ Nuovo", use_container_width=True):
        st.session_state.page = "cliente"

st.divider()

# =========================
# CARD
# =========================
def card(title, value):
    return f"""
    <div style="padding:14px;border-radius:14px;background:#111827;
    color:white;text-align:center;margin:6px 0;">
        <div style="font-size:12px;opacity:0.7;">{title}</div>
        <div style="font-size:20px;font-weight:600">{value}</div>
    </div>
    """

# =========================================================
# 📊 DASHBOARD
# =========================================================
if st.session_state.page == "dashboard":

    st.markdown("## ⛽ Dashboard operativa")

    prezzo_base = st.number_input(
        "⛽ Prezzo base",
        value=float(st.session_state.prezzo_base),
        step=0.001,
        format="%.3f"
    )

    st.session_state.prezzo_base = prezzo_base

    clienti_count = len(df)

    media_margine = round(df["Margine"].mean(), 3) if not df.empty else 0

    prezzo_medio = (
        calc_price(prezzo_base, df["Margine"].mean(), df["Trasporto"].mean())
        if not df.empty else prezzo_base
    )

    st.markdown(card("⛽ Base", format_euro(prezzo_base)), unsafe_allow_html=True)
    st.markdown(card("👤 Clienti", clienti_count), unsafe_allow_html=True)

    st.divider()

    # EMAIL TEMPLATE
    st.markdown("### ✉️ Email")
    template = st.text_area("Email template", value=st.session_state.email_template, height=250)
    st.session_state.email_template = template

    # WHATSAPP TEMPLATE
    st.markdown("### 💬 WhatsApp")
    wa_template = st.text_area("WhatsApp template", value=st.session_state.whatsapp_template, height=120)
    st.session_state.whatsapp_template = wa_template

    st.divider()

# =========================================================
# LISTA CLIENTI (WHATSAPP FIX QUI)
# =========================================================
    st.markdown("### 👤 Clienti")

    search_dash = st.text_input("🔍 Cerca", key="search_dashboard")
    df_view = filtra_clienti(df, search_dash)

    for _, c in df_view.iterrows():

        prezzo = calc_price(prezzo_base, c["Margine"], c["Trasporto"])

        data = datetime.now().strftime("%d/%m/%Y")

        msg = wa_template\
            .replace("{prezzo}", format_euro(prezzo))\
            .replace("{nome}", c["Nome"])\
            .replace("{data}", data)

        wa = f"https://wa.me/{str(c['Telefono']).replace('+','').replace(' ','')}?text={msg}"
        wa = wa.replace(" ", "%20").replace("\n", "%0A")

        st.markdown(f"### {c['Nome']}")
        st.markdown(f"[📲 WhatsApp]({wa})")
        st.divider()

# =========================================================
# CLIENTI + CLIENTE (resto invariato)
# =========================================================
elif st.session_state.page == "clienti":
    st.markdown("## 👤 Clienti")

elif st.session_state.page == "cliente":
    st.markdown("## ➕ Cliente")
